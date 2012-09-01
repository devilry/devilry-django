#from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



class TestGradeEditorWidget(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _browseToAssignment(self, id):
        self.browseTo('/assignment/{id}/'.format(id=id))

    def _loginToAssignment(self, username, id):
        self.loginTo(username, '/assignment/{id}/'.format(id=id))

    def test_shortcuts_render(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:admin(week2admin)'])
        assignmentid = self.testhelper.sub_period1_week2.id
        self._loginToAssignment('week2admin', assignmentid)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditorselect_widget')
        title = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget .editablesidebarbox_title').text.strip()
        body = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget .editablesidebarbox_body').text.strip()
        self.assertTrue(title.startswith('Grade editor'))
        self.assertEquals(body, 'Approved/not approved')
        editlink = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget a.edit_link')
        editurl = '#/assignment/{id}/@@grade-editor/'.format(id=assignmentid)
        self.assertTrue(editlink.get_attribute('href').endswith(editurl))
