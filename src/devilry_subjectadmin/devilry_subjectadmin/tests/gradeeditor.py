import json
#from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



class TestGradeEditorWidget(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _loginToAssignment(self, username, id):
        self.loginTo(username, '/assignment/{id}/'.format(id=id))

    def test_render(self):
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
        editpath = '/assignment/{id}/@@grade-editor/'.format(id=assignmentid)
        self.assertEquals(editlink.get_attribute('href').split('#')[1],
                        editpath)



class TestGradeEditorEdit(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:admin(week2admin)'])
        self.assignmentid = self.testhelper.sub_period1_week2.id

    def _loginToGradeEditorEdit(self, username, id):
        self.loginTo(username, '/assignment/{id}/@@grade-editor/'.format(id=id))
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditoredit')

    def _find_element(self, cssselector):
        cssselector = '.devilry_subjectadmin_gradeeditoredit {0}'.format(cssselector)
        return self.selenium.find_element_by_css_selector(cssselector)

    def _find_elements(self, cssselector):
        cssselector = '.devilry_subjectadmin_gradeeditoredit {0}'.format(cssselector)
        return self.selenium.find_elements_by_css_selector(cssselector)

    def test_render_gradeeditor_info(self):
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.current_gradeeditor_info')
        self.assertEquals(self._find_element('.current_gradeeditor_info .registryitem_title').text.strip(),
                          'Approved/not approved')
        description = self._find_element('.current_gradeeditor_info .registryitem_description').text.strip()
        self.assertTrue(description.startswith('A simple gradeeditor that'))
        changehref = self._find_element('.current_gradeeditor_info .change_gradeeditor_link').get_attribute('href')
        changepath = '/assignment/{id}/@@grade-editor/change'.format(id=self.assignmentid)
        self.assertEquals(changehref.split('#')[1], changepath)

    def test_render_what_is(self):
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        title = self._find_element('.what_is_a_gradeeditor_help h3').text.strip()
        self.assertEquals(title, 'What is a Grade editor?')

    def test_return_to_assignmentlink(self):
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.return_to_assignmentlink')
        href = self._find_element('.return_to_assignmentlink').get_attribute('href')
        assignmentpath = '/assignment/{id}/'.format(id=self.assignmentid)
        self.assertEquals(href.split('#')[1], assignmentpath)

    def test_gradeeditor_with_config(self):
        config = self.testhelper.sub_period1_week2.gradeeditor_config
        config.gradeeditorid = 'asminimalaspossible'
        config.config = json.dumps({'defaultvalue': True,
                                    'fieldlabel': 'This is a test'})
        config.save()
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.devilry_gradeconfigeditor')
        self.assertEquals(len(self._find_elements('.missing_config')), 0)
        textinput = self._find_element('.devilry_gradeconfigeditor input[type=text]')
        self.assertEquals(textinput.get_attribute('value'), 'This is a test')

    def test_gradeeditor_missing_config(self):
        config = self.testhelper.sub_period1_week2.gradeeditor_config
        config.gradeeditorid = 'asminimalaspossible'
        config.config = ''
        config.save()
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.current_gradeeditor_info')
        self.assertEquals(len(self._find_elements('.missing_config')), 1)




class TestGradeEditorMixin(object):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:admin(week2admin)'])
        self.assignmentid = self.testhelper.sub_period1_week2.id

    def loginAndLoad(self):
        self.loginTo('week2admin', '/assignment/{id}/@@grade-editor/'.format(id=self.assignmentid))
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditoredit')

    def find_element(self, cssselector):
        cssselector = '.devilry_subjectadmin_gradeeditoredit .devilry_gradeconfigeditor {0}'.format(cssselector)
        return self.selenium.find_element_by_css_selector(cssselector)

    def set_config(self, gradeeditorid, configstring):
        config = self.testhelper.sub_period1_week2.gradeeditor_config
        config.gradeeditorid = 'asminimalaspossible'
        config.config = json.dumps({'defaultvalue': True,
                                    'fieldlabel': 'This is a test'})
        config.save()

    def set_json_config(self, gradeeditorid, configobj):
        self.set_config(gradeeditorid, json.dumps(configobj))

    def waitForConfigEditor(self):
        self.waitForCssSelector('.devilry_gradeconfigeditor')


class TestAsMinimalAsPossibleGradeEditor(TestGradeEditorMixin, SubjectAdminSeleniumTestCase):
    def test_sanity(self):
        self.set_json_config('asminimalaspossible', {'defaultvalue': True,
                                                     'fieldlabel': 'This is a test'})
        self.loginAndLoad()
        self.waitForConfigEditor()
        textinput = self.find_element('input[type=text]')
        self.assertEquals(textinput.get_attribute('value'), 'This is a test')
