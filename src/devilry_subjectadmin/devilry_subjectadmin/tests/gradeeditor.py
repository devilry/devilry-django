import json
#from devilry.apps.core.models import Assignment
from devilry.apps.gradeeditors.models import Config
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

    def _set_config(self, assignment, gradeeditorid, configstring):
        config = assignment.gradeeditor_config
        config.gradeeditorid = gradeeditorid
        config.config = configstring
        config.save()

    def _set_json_config(self, assignment, gradeeditorid, configobj):
        configstring = json.dumps(configobj)
        self._set_config(assignment, gradeeditorid, configstring)

    def test_gradeeditor_with_config(self):
        self._set_json_config(self.testhelper.sub_period1_week2,
                              'asminimalaspossible',
                              {'defaultvalue': True,
                                    'fieldlabel': 'This is a test'})
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.devilry_gradeconfigeditor')
        self.assertEquals(len(self._find_elements('.missing_config')), 0)
        textinput = self._find_element('.devilry_gradeconfigeditor input[type=text]')
        self.assertEquals(textinput.get_attribute('value'), 'This is a test')

    def test_gradeeditor_missing_config(self):
        self._set_config(self.testhelper.sub_period1_week2,
                         'asminimalaspossible', configstring=None)
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.current_gradeeditor_info')
        self.assertEquals(len(self._find_elements('.missing_config')), 1)

    def test_gradeeditor_cancel(self):
        self._set_config(self.testhelper.sub_period1_week2,
                         'asminimalaspossible', configstring=None)
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.cancel_edit_config_button')
        self._find_element('.cancel_edit_config_button').click()
        # If the page is not changed, this will fail
        assignmenturl = self.get_absolute_url('/assignment/{id}/'.format(id=self.assignmentid))
        self.waitFor(self.selenium, lambda s: s.current_url == assignmenturl)

    def test_gradeeditor_save_and_continue_editing(self):
        self._set_config(self.testhelper.sub_period1_week2,
                         'asminimalaspossible', configstring=None)
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.save_and_continue_editing_button')
        self.assertEquals(len(self._find_elements('.missing_config')), 1)
        self._find_element('.save_and_continue_editing_button').click()
        before_save_url = self.selenium.current_url
        self.waitFor(self.selenium, lambda s: len(self._find_elements('.missing_config')) == 0)
        self.assertEquals(self.selenium.current_url, before_save_url) # We are still on the same page



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

    def perform_save(self):
        savebutton = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditoredit .devilry_extjsextras_savebutton')
        savebutton.click()
        self.waitFor(self.selenium, lambda s: not s.current_url.endswith('@@grade-editor/'))

    def set_config(self, gradeeditorid, configstring):
        config = self.testhelper.sub_period1_week2.gradeeditor_config
        config.gradeeditorid = gradeeditorid
        config.config = configstring
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
        textinput.clear()
        textinput.send_keys('Updated')
        self.perform_save()
        config = Config.objects.get(assignment_id=self.assignmentid)
        self.assertEquals(json.loads(config.config), {'defaultvalue': True,
                                                      'fieldlabel': 'Updated'})
