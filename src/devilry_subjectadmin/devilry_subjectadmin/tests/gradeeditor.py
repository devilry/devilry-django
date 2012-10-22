import json
from devilry.apps.core.models import Assignment
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
        title = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget .titlebox h4').text.strip()
        body = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget .markupmoreinfobox').text.strip()
        self.assertTrue(title.startswith('Grading system'))
        self.assertTrue(body.startswith('Approved/not approved'))
        editlink = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditorselect_widget a.edit_link')
        editpath = '/assignment/{id}/@@grade-editor/'.format(id=assignmentid)
        self.assertEquals(editlink.get_attribute('href').split('#')[1],
                        editpath)



class SetConfigMixin(object):
    def set_config(self, assignment, gradeeditorid, configstring):
        config = assignment.gradeeditor_config
        config.gradeeditorid = gradeeditorid
        config.config = configstring
        config.save()

    def set_json_config(self, assignment, gradeeditorid, configobj):
        configstring = json.dumps(configobj)
        self.set_config(assignment, gradeeditorid, configstring)


class TestGradeEditorEdit(SubjectAdminSeleniumTestCase, SetConfigMixin):
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
        self.assertEquals(title, 'What is a grading system?')

    def test_return_to_assignmentlink(self):
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.return_to_assignmentlink')
        href = self._find_element('.return_to_assignmentlink').get_attribute('href')
        assignmentpath = '/assignment/{id}/'.format(id=self.assignmentid)
        self.assertEquals(href.split('#')[1], assignmentpath)

    def test_gradeeditor_with_config(self):
        self.set_json_config(self.testhelper.sub_period1_week2,
                              'asminimalaspossible',
                              {'defaultvalue': True,
                                    'fieldlabel': 'This is a test'})
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.devilry_gradeconfigeditor')
        self.assertEquals(len(self._find_elements('.missing_config')), 0)
        textinput = self._find_element('.devilry_gradeconfigeditor input[type=text]')
        self.assertEquals(textinput.get_attribute('value'), 'This is a test')

    def test_gradeeditor_missing_config(self):
        self.set_config(self.testhelper.sub_period1_week2,
                        'asminimalaspossible', configstring='')
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.current_gradeeditor_info')
        self.assertEquals(len(self._find_elements('.missing_config')), 1)

    def test_gradeeditor_cancel(self):
        self.set_config(self.testhelper.sub_period1_week2,
                        'asminimalaspossible', configstring='')
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.cancel_edit_config_button')
        self._find_element('.cancel_edit_config_button').click()
        # If the page is not changed, this will fail
        assignmenturl = self.get_absolute_url('/assignment/{id}/'.format(id=self.assignmentid))
        self.waitFor(self.selenium, lambda s: s.current_url == assignmenturl)

    def test_gradeeditor_save_and_continue_editing(self):
        self.set_config(self.testhelper.sub_period1_week2,
                        'asminimalaspossible', configstring='')
        self._loginToGradeEditorEdit('week2admin', self.assignmentid)
        self.waitForCssSelector('.save_and_continue_editing_button')
        self.assertEquals(len(self._find_elements('.missing_config')), 1)
        self._find_element('.save_and_continue_editing_button').click()
        before_save_url = self.selenium.current_url
        self.waitFor(self.selenium, lambda s: len(self._find_elements('.missing_config')) == 0)
        self.assertEquals(self.selenium.current_url, before_save_url) # We are still on the same page



class TestGradeEditorChange(SubjectAdminSeleniumTestCase, SetConfigMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:admin(week2admin)'])
        self.assignment = self.testhelper.sub_period1_week2

    def _loginAndLoad(self):
        self.loginTo('week2admin', '/assignment/{id}/@@grade-editor/change'.format(id=self.assignment.id))
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditorchange')
        self._wait_for_gridload()

    def _find_element(self, cssselector):
        cssselector = '.devilry_subjectadmin_gradeeditorchange {0}'.format(cssselector)
        return self.selenium.find_element_by_css_selector(cssselector)

    def _find_elements(self, cssselector):
        cssselector = '.devilry_subjectadmin_gradeeditorchange {0}'.format(cssselector)
        return self.selenium.find_elements_by_css_selector(cssselector)

    def _find_gridrows(self):
        return self._find_elements('.devilry_subjectadmin_gradeeditorchoosegrid .x-grid-row')

    def _wait_for_gridload(self):
        self.waitFor(self.selenium, lambda s: len(self._find_gridrows()) > 0)

    def _get_savebutton(self):
        savebutton = self._find_element('.devilry_extjsextras_savebutton button')
        return savebutton

    def _perform_save(self):
        self.waitFor(self.selenium, lambda s: self._get_savebutton().is_enabled())
        self._get_savebutton().click()
        self.waitFor(self.selenium, lambda s: s.current_url.endswith('@@grade-editor/'))
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditoredit')

    def test_render(self):
        self.set_config(self.assignment, 'asminimalaspossible', '')
        self._loginAndLoad()
        self.assertTrue('Select a grading system' in self.selenium.page_source)
        selected = self._find_element('.devilry_subjectadmin_gradeeditorchoosegrid .x-grid-row-selected')
        self.assertEquals(len(selected.find_elements_by_css_selector('.gradeeditorid_asminimalaspossible')), 1)
        savebutton = self._get_savebutton()
        self.assertFalse(savebutton.is_enabled())

    def _get_row_by_gradeeditorid(self, gradeeditorid):
        for row in self._find_gridrows():
            matches = row.find_elements_by_css_selector('.gradeeditorid_{id}'.format(id=gradeeditorid))
            if len(matches) > 0:
                return row

    def _get_config(self):
        return Assignment.objects.get(id=self.assignment.id).gradeeditor_config

    def test_change(self):
        self.set_config(self.assignment, 'asminimalaspossible', '')
        self._loginAndLoad()
        self._get_row_by_gradeeditorid('approved').click()
        self._perform_save()
        config = self._get_config()
        self.assertEquals(config.gradeeditorid, 'approved')
        self.assertEquals(config.config, '')

    def test_change_existing_config(self):
        self.set_json_config(self.assignment, 'asminimalaspossible',
                             {'defaultvalue': True,
                              'fieldlabel': 'This is a test'})
        self._loginAndLoad()
        self.assertFalse(self._get_savebutton().is_enabled())
        self._get_row_by_gradeeditorid('approved').click()
        self.waitFor(self.selenium, lambda s: not self._get_savebutton().is_enabled()) # If this times out, the button have been enabled by choosing another grade editor, which should not happen before we have confirmed overwriting config

        self.waitForCssSelector('.clear_config_confirm')
        self._find_element('.clear_config_confirm input[type="button"]').click() # check the confirm checkbox
        self.waitFor(self.selenium, lambda s: self._get_savebutton().is_enabled())

        self._perform_save()
        config = self._get_config()
        self.assertEquals(config.gradeeditorid, 'approved')
        self.assertEquals(config.config, '')

    def test_cancel(self):
        self._loginAndLoad()
        self.waitForCssSelector('.cancel_gradeeditor_change_button')
        self._find_element('.cancel_gradeeditor_change_button').click()
        # If the page is not changed, this will fail
        editurl = self.get_absolute_url('/assignment/{id}/@@grade-editor/'.format(id=self.assignment.id))
        self.waitFor(self.selenium, lambda s: s.current_url == editurl)


class TestGradeEditorMixin(SetConfigMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:admin(week2admin)'])
        self.assignment = self.testhelper.sub_period1_week2

    def loginAndLoad(self):
        self.loginTo('week2admin', '/assignment/{id}/@@grade-editor/'.format(id=self.assignment.id))
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditoredit')

    def wait_for_element(self, cssselector):
        configeditor = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_gradeeditoredit .devilry_gradeconfigeditor')
        return self.waitForAndFindElementByCssSelector(cssselector, within=configeditor)

    def perform_save(self):
        savebutton = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_gradeeditoredit .devilry_extjsextras_savebutton')
        savebutton.click()
        self.waitFor(self.selenium, lambda s: not s.current_url.endswith('@@grade-editor/'))

    def waitForConfigEditor(self):
        self.waitForCssSelector('.devilry_subjectadmin_gradeeditoredit .devilry_gradeconfigeditor')


class TestAsMinimalAsPossibleGradeEditor(TestGradeEditorMixin, SubjectAdminSeleniumTestCase):
    def test_sanity(self):
        self.set_json_config(self.assignment, 'asminimalaspossible',
                             {'defaultvalue': True,
                              'fieldlabel': 'This is a test'})
        self.loginAndLoad()
        textinput = self.wait_for_element('input[type=text]')
        self.assertEquals(textinput.get_attribute('value'), 'This is a test')
        textinput.clear()
        textinput.send_keys('Updated')
        self.perform_save()
        config = Config.objects.get(assignment_id=self.assignment.id)
        self.assertEquals(json.loads(config.config), {'defaultvalue': True,
                                                      'fieldlabel': 'Updated'})
