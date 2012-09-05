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



class TestManageSingleGroupOverview(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.top_infobox')
        top_infobox = self.find_element('.top_infobox')
        self.assertTrue(top_infobox.text.strip().startswith('Hold down CMD to select more groups.'))
