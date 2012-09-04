from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup

from .base import SubjectAdminSeleniumTestCase



class TestManageMultipleStudentsMixin(object):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1


    def browseToAndSelectAs(self, username, select_groups=[]):
        select_ids = ','.join([str(group.id) for group in select_groups])
        path = '/assignment/{0}/@@manage-students/@@select/{1}'.format(self.assignment.id,
                                                                       select_ids)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_multiplegroupsview')

    def create_group(self, groupspec):
        self.testhelper.add_to_path('uni;sub.p1.a1.{0}'.format(groupspec))
        groupname = groupspec.split('.')[0].split(':')[0]
        return getattr(self.testhelper, 'sub_p1_a1_{0}'.format(groupname))

    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_multiplegroupsview {0}'.format(cssselector))


class TestManageMultipleStudentsOverview(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.top_infobox')
        top_infobox = self.find_element('.top_infobox')
        self.assertEquals(top_infobox.text.strip(),
                          '2/2 groups selected. Hold down CMD to select more groups.')


class TestManageMultipleStudentsCreateProjectGroups(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        self.waitForCssSelector('.merge_groups_helpbox')
        button = self.find_element('.merge_groups_button')
        help = self.find_element('.merge_groups_helpbox')
        self.assertTrue(button.text.strip().startswith('Create project group'))
        self.assertTrue(help.text.strip().startswith('Merge the selected groups into a single group'))

    def test_show_and_hide(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        self.waitForCssSelector('.merge_groups_helpbox')
        buttonEl = self.find_element('.merge_groups_button button')
        help = self.find_element('.merge_groups_helpbox')
        confirmContainer = self.find_element('.merge_groups_confirmcontainer')

        self.assertFalse(confirmContainer.is_displayed())
        self.assertTrue(help.is_displayed())
        buttonEl.click()
        self.waitFor(help, lambda h: not h.is_displayed()) # Wait for help to be hidden
        self.waitFor(confirmContainer, lambda c: c.is_displayed()) # Wait for confirm to be displayed

        cancelButtonEl = self.find_element('.merge_groups_cancel_button')
        cancelButtonEl.click()
        self.waitFor(confirmContainer, lambda c: not c.is_displayed()) # Wait for confirm to be hidden
        self.waitFor(help, lambda h: h.is_displayed()) # Wait for help to be displayed

    def test_create_project_group(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        buttonEl = self.find_element('.merge_groups_button button')
        confirmContainer = self.find_element('.merge_groups_confirmcontainer')
        buttonEl.click()
        self.waitFor(confirmContainer, lambda c: c.is_displayed()) # Wait for confirm to be displayed

        createButtonEl = self.find_element('.merge_groups_confirm_button')
        createButtonEl.click()
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.devilry_subjectadmin_singlegroupview')) == 1)
        self.assertFalse(AssignmentGroup.objects.filter(id=g2.id).exists())
        g1 = self.testhelper.reload_from_db(g1)
        candidates = set([c.student.username for c in g1.candidates.all()])
        self.assertEquals(candidates, set(['student1', 'student2']))
