from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestCreateNewAssignment(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_chooseperiod_render(self):
        self.browseToTest('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.activeperiodslist')
        self.assertTrue('duck-mek2030.2012h' in self.driver.page_source)
        self.assertTrue('duck1100.2011h' in self.driver.page_source)
        self.assertTrue('subjectadmin.createnewassignment.title' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.activeperiod.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.activeperiod.label' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.delivery_types.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.delivery_types.label' in self.driver.page_source)
        self.assertTrue('themebase.next' in self.driver.page_source)

    def test_chooseperiod_first_checked(self):
        self.browseToTest('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.activeperiodslist input[aria-checked=true]') # NOTE: We wait for aria-checked because just waiting for activeperiodslist may lead to timing miss when waiting for focus.
        radioButtons = self.driver.find_elements_by_css_selector('.activeperiodslist input[role=radio]')
        self.assertEquals(radioButtons[0].get_attribute('aria-checked'), 'true')
        self.assertEquals(radioButtons[1].get_attribute('aria-checked'), 'false')


    def test_chooseperiod_no_periods(self):
        url = self.getJsAppTestUrl(self.appname) + '?loadNoPeriods=yes#/@@create-new-assignment/@@chooseperiod'
        self.driver.get(url)
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('subjectadmin.assignment.error.no_active_periods' in self.driver.page_source)

    def test_form_render(self):
        self.browseToTest('/@@create-new-assignment/1,0')
        self.waitForCssSelector('.createnewassignmentform')

        self.assertTrue('subjectadmin.createnewassignment.title' in self.driver.page_source)
        self.assertTrue('themebase.create' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.long_name.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.long_name.label' in self.driver.page_source)

        self.assertTrue('subjectadmin.assignment.short_name.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.short_name.label' in self.driver.page_source)

    def test_form_render_advanced_fieldset(self):
        self.browseToTest('/@@create-new-assignment/1,0')
        self.waitForCssSelector('.createnewassignmentform')

        self.assertFalse('subjectadmin.assignment.anonymous.label' in self.driver.page_source)
        self.assertFalse('subjectadmin.assignment.publishing_time.label' in self.driver.page_source)
        self.assertFalse('subjectadmin.assignment.add_all_relatedstudents.label' in self.driver.page_source)
        self.assertFalse('subjectadmin.assignment.autosetup_examiners.label' in self.driver.page_source)

        fieldsetbutton = self.driver.find_element_by_css_selector('fieldset.advanced_options_fieldset>legend>div.x-tool')
        fieldsetbutton.click()

        self.assertTrue('subjectadmin.assignment.anonymous.label' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.anonymous.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.publishing_time.label' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.publishing_time.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.add_all_relatedstudents.label' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.add_all_relatedstudents.help' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.autosetup_examiners.label' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.autosetup_examiners.help' in self.driver.page_source)


    def _set_value(self, fieldname, value):
        field = self.driver.find_element_by_css_selector('input[name={0}]'.format(fieldname))
        field.send_keys(value)

    def test_form_createbutton(self):
        self.browseToTest('/@@create-new-assignment/1,0')
        self.waitForCssSelector('.createnewassignmentform')

        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self.assertFalse(createbutton.is_enabled())

        # Make sure the create button is clickable after both short and long names are entered.
        self._set_value('long_name', 'Test')
        self.assertFalse(createbutton.is_enabled())

        self._set_value('short_name', 'test')
        self.waitForEnabled(createbutton)

    def test_form_servererror(self):
        self.browseToTest('/@@create-new-assignment/1,0')
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
        self.browseToTest('/@@create-new-assignment/1,0')
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
        self.browseToTest('/@@create-new-assignment/3,0')
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

    def test_form_responseData_not_active_period(self):
        self.browseToTest('/@@create-new-assignment/100,0')
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('subjectadmin.assignment.error.not_active_period' in self.driver.page_source)

    def test_success(self):
        self.browseToTest('/@@create-new-assignment/1,0')
        self.waitForCssSelector('.createnewassignmentform')

        self._set_value('long_name', 'Test')
        self._set_value('short_name', 'sometest')
        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self.waitForEnabled(createbutton)
        createbutton.click()

        self.waitForCssSelector('.createnewassignment-successpanel')
        links = self.driver.find_elements_by_css_selector('.actionlist a')
        self.assertEquals(len(links), 3)
        self.assertEquals(links[0].text, u'subjectadmin.createnewassignment.success.gotocreated')
        self.assertEquals(links[0].get_attribute('href'), 'http://localhost:8000/subjectadmin/test#/duck1100/2012h/sometest')
        self.assertEquals(links[1].text, u'subjectadmin.createnewassignment.success.addanother')
        self.assertEquals(links[1].get_attribute('href'), u'http://localhost:8000/subjectadmin/test#/@@create-new-assignment/@@chooseperiod')
        self.assertEquals(links[2].text, u'subjectadmin.createnewassignment.success.addanother-similar')
        self.assertEquals(links[2].get_attribute('href'), u'http://localhost:8000/subjectadmin/test#/@@create-new-assignment/1,0')

    def test_success_direct(self):
        self.browseToTest('/@@create-new-assignment/@@success')
        self.waitForCssSelector('.x-message-box')
        self.assertTrue('This page is only available after creating a new assignment.' in self.driver.page_source)

    def test_success_addanother(self):
        self.browseToTest('/@@create-new-assignment/1,0')
        self.waitForCssSelector('.createnewassignmentform')

        self._set_value('long_name', 'Test')
        self._set_value('short_name', 'sometest')
        createbutton = self.driver.find_element_by_css_selector('.createbutton button')
        self.waitForEnabled(createbutton)
        createbutton.click()
        self.waitForCssSelector('.createnewassignment-successpanel')
        links = self.driver.find_elements_by_css_selector('.actionlist a')
        links[1].click()

        self.waitForCssSelector('.activeperiodslist input[aria-checked=true]') # NOTE: We wait for aria-checked because just waiting for activeperiodslist may lead to timing miss when waiting for focus.
        radioButtons = self.driver.find_elements_by_css_selector('.activeperiodslist input[role=radio]')
        self.assertEquals(radioButtons[0].get_attribute('aria-checked'), 'false')
        self.assertEquals(radioButtons[1].get_attribute('aria-checked'), 'true')
