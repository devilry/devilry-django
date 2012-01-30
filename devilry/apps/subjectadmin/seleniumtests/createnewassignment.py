from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase
import time


class TestCreateNewAssignment(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_chooseperiod_render(self):
        self.browseToTest('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.activeperiodslist')
        self.assertTrue('duck-mek2030.2012h' in self.driver.page_source)
        self.assertTrue('duck1100.2011h' in self.driver.page_source)
        self.assertTrue('subjectadmin.chooseperiod.title' in self.driver.page_source)
        self.assertTrue('subjectadmin.chooseperiod.sidebarhelp' in self.driver.page_source)
        self.assertTrue('themebase.next' in self.driver.page_source)
        periodlist = self.driver.find_element_by_class_name('activeperiodslist')
        self.assertEquals(len(periodlist.find_elements_by_css_selector('tr.x-grid-row')), 3)

    def test_chooseperiod_nextbutton(self):
        self.browseToTest('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.nextbutton')
        buttonel = self.driver.find_element_by_css_selector('.nextbutton button')
        self.assertFalse(buttonel.is_enabled())

        # Click first element in the periodlist and make sure nextbutton is enabled afterwards
        periodlist = self.driver.find_element_by_class_name('activeperiodslist')
        firstperiod = periodlist.find_elements_by_css_selector('tr.x-grid-row')[0]
        firstperiod.click()
        self.assertTrue(buttonel.is_enabled())

    def test_form_render(self):
        self.browseToTest('/@@create-new-assignment/1')
        self.waitForCssSelector('.createnewassignmentform')

        self.assertTrue('subjectadmin.createnewassignment.title' in self.driver.page_source)
        self.assertTrue('subjectadmin.createnewassignment.sidebarhelp' in self.driver.page_source)
        self.assertTrue('themebase.create' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.long_name.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.long_name.label' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.delivery_types.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.delivery_types.label' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.short_name.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.short_name.label' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.publishing_time.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.publishing_time.label' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.anonymous.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.anonymous.label' in self.driver.page_source)


    def _set_value(self, fieldname, value):
        field = self.driver.find_element_by_css_selector('input[name={0}]'.format(fieldname))
        field.send_keys(value)

    def test_form_createbutton(self):
        self.browseToTest('/@@create-new-assignment/1')
        self.waitForCssSelector('.createnewassignmentform')

        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self.assertFalse(createbutton.is_enabled())

        # Make sure the create button is clickable after both short and long names are entered.
        self._set_value('long_name', 'Test')
        self.assertFalse(createbutton.is_enabled())

        self._set_value('short_name', 'test')
        self.waitForEnabled(createbutton)

    def test_form_servererror(self):
        self.browseToTest('/@@create-new-assignment/1')
        self.waitForCssSelector('.createnewassignmentform')
        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self._set_value('long_name', 'Just to enable the button')

        # subjectadmin.model.AssignmentTestMock defines special values for short_name to produce error messages ...
        self._set_value('short_name', 'servererror')
        self.waitForEnabled(createbutton)
        createbutton.click()
        self.waitForCssSelector('.alert-message')
        self.assertTrue('500: Server error' in self.driver.page_source)

    def test_form_lostconnectionerror(self):
        self.browseToTest('/@@create-new-assignment/1')
        self.waitForCssSelector('.createnewassignmentform')
        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self._set_value('long_name', 'Just to enable the button')

        # subjectadmin.model.AssignmentTestMock defines special values for short_name to produce error messages ...
        self._set_value('short_name', 'noconnection')
        self.waitForEnabled(createbutton)
        createbutton.click()
        self.waitForCssSelector('.alert-message')
        self.assertTrue('themebase.lostserverconnection' in self.driver.page_source)

    def test_form_responseData_errors(self):
        self.browseToTest('/@@create-new-assignment/3')
        self.waitForCssSelector('.createnewassignmentform')
        createbutton = self.driver.find_element_by_css_selector('.createbutton button')

        self._set_value('long_name', 'Just to enable the button')
        self._set_value('short_name', 'unused')
        self.waitForEnabled(createbutton)
        createbutton.click()

        # subjectadmin.model.AssignmentTestMock defines special values for short_name to produce error messages ...
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('This is a global error message' in self.driver.page_source)
        self.assertTrue('Another global message' in self.driver.page_source)
        self.assertFalse('This should not be shown' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.short_name.label:</strong> Invalid short name' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.long_name.label:</strong> Invalid. Long name' in self.driver.page_source)
        self.assertTrue('' in self.driver.page_source)

    def test_jasmine(self):
        self.runJasmineTests()
