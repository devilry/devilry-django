from selenium.common.exceptions import StaleElementReferenceException
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup

from .base import SubjectAdminSeleniumTestCase



class TestManageSingleGroupMixin(object):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1


    def browseToAndSelectAs(self, username, select_group):
        path = '/assignment/{0}/@@manage-students/@@select/{1}'.format(self.assignment.id,
                                                                       select_group.id)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_singlegroupview')

    def create_group(self, groupspec):
        self.testhelper.add_to_path('uni;sub.p1.a1.{0}'.format(groupspec))
        groupname = groupspec.split('.')[0].split(':')[0]
        return getattr(self.testhelper, 'sub_p1_a1_{0}'.format(groupname))

    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_singlegroupview {0}'.format(cssselector))
    def find_elements(self, cssselector):
        return self.selenium.find_elements_by_css_selector('.devilry_subjectadmin_singlegroupview {0}'.format(cssselector))

    def find_listofgroups_rows(self, selected_only=False):
        cssselector = '.devilry_subjectadmin_listofgroups .x-grid-row'
        if selected_only:
            cssselector += '-selected'
        return self.selenium.find_elements_by_css_selector(cssselector)



class TestManageSingleGroupOverview(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.top_infobox')
        top_infobox = self.find_element('.top_infobox')
        self.assertTrue(top_infobox.text.strip().startswith('Hold down CMD to select more groups.'))



class TestManageSingleGroupStudents(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def _find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_studentsingroupgrid .x-grid-row')

    def test_render(self):
        self.testhelper.create_user('student1', fullname='Student One')
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsonsingle')
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        fullname = self.find_element('.studentsingroupgrid_meta_student1 .fullname')
        username = self.find_element('.studentsingroupgrid_meta_student1 .username')
        self.assertTrue(fullname.text.strip(), 'Student One')
        self.assertTrue(username.text.strip(), 'student1')

    def test_missing_fullname(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsonsingle')
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        missing = self.find_element('.studentsingroupgrid_meta_student1 .fullname .nofullname')
        username = self.find_element('.studentsingroupgrid_meta_student1 .username')
        self.assertTrue(missing.text.strip(), 'Full name missing')
        self.assertTrue(username.text.strip(), 'student1')

    def test_no_removebutton_on_single(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_remove')), 0)

    def _pop_by_username(self, username):
        cssselector = '.studentsingroupgrid_remove_{0}'.format(username)
        self.waitForCssSelector(cssselector)
        self.find_element(cssselector).click()

        # Confirm delete
        self.waitForCssSelector('#single_students_confirm_pop .okbutton')
        okbutton = self.find_element('#single_students_confirm_pop .okbutton')
        self.waitFor(okbutton, lambda b: okbutton.is_displayed())
        okbutton.click()

        # After pop, the original and the split group will be marked in the multi-view
        self.waitForCssSelector('.devilry_subjectadmin_multiplegroupsview')
        self.assertEquals(len(self.find_listofgroups_rows(selected_only=True)), 2)

    def test_pop(self):
        g1 = self.create_group('g1:candidate(student1,student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_remove')), 2)
        self._pop_by_username('student2')

    def test_pop_cancel(self):
        g1 = self.create_group('g1:candidate(student1,student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_remove')), 2)

        cssselector = '.studentsingroupgrid_remove_student1'
        self.waitForCssSelector(cssselector)
        self.find_element(cssselector).click()

        # Cancel
        cancelbutton = self.find_element('#single_students_confirm_pop .cancelbutton')
        self.waitFor(cancelbutton, lambda b: cancelbutton.is_displayed())
        cancelbutton.click()
        meta = self.find_element('.studentsingroupgrid_meta_student1')
        self.waitFor(meta, lambda m: meta.is_displayed())
