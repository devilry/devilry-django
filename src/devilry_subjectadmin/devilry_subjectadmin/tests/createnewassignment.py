from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


class TestCreateNewAssignment(SubjectAdminSeleniumTestCase):
    appname = 'subjectadmin'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.login('grandma')

        self.testhelper.add(nodes='uni',
                            subjects=['duck1100'],
                            periods=['2012h'])
        self.period_id = self.testhelper.duck1100_2012h.id

    def test_form_render(self):
        self.browseTo('/@@create-new-assignment/{0}'.format(self.period_id))
        self.waitForCssSelector('.createnewassignmentform')

        self.assertTrue('Create new assignment' in self.selenium.page_source)

        self.assertTrue('Long name' in self.selenium.page_source)
        self.assertTrue('Example of assignment long name' in self.selenium.page_source)
        self.assertTrue('Choose a descriptive name for your assignment' in self.selenium.page_source)

        self.assertTrue('Choose a short name with at most 20 letters for your assignment' in self.selenium.page_source)
        self.assertTrue('Short name' in self.selenium.page_source)
        self.assertTrue('How do students add deliveries?' in self.selenium.page_source)

    def test_invalid_period(self):
        self.browseTo('/@@create-new-assignment/1001')
        self.waitForCssSelector('.createnewassignmentform')
        self.assertTrue('Period 1001 is not an active period.' in self.selenium.page_source)

    def test_form_render_advanced_fieldset(self):
        self.browseTo('/@@create-new-assignment/{0}'.format(self.period_id))
        self.waitForCssSelector('.createnewassignmentform')
        self.assertTrue('Advanced options' in self.selenium.page_source)

        self.assertFalse('Anonymous?' in self.selenium.page_source)
        self.assertFalse('Publishing time' in self.selenium.page_source)
        self.assertFalse('Add all students to this assignment?' in self.selenium.page_source)
        self.assertFalse('Automatically setup examiners?' in self.selenium.page_source)

        fieldsetbutton = self.selenium.find_element_by_css_selector('fieldset.advanced_options_fieldset>legend>div.x-tool')
        fieldsetbutton.click()

        self.assertTrue('Anonymous?' in self.selenium.page_source)
        self.assertTrue('If an assignment is anonymous, examiners see a candidate-id instead of a username' in self.selenium.page_source)
        self.assertTrue('Publishing time' in self.selenium.page_source)
        self.assertTrue('Add all students to this assignment?' in self.selenium.page_source)
        self.assertTrue('Automatically setup examiners?' in self.selenium.page_source)


    def _set_value(self, fieldname, value):
        field = self.selenium.find_element_by_css_selector('input[name={0}]'.format(fieldname))
        field.send_keys(value)

    def test_form_createbutton(self):
        self.browseTo('/@@create-new-assignment/{0}'.format(self.period_id))
        self.waitForCssSelector('.createnewassignmentform')

        createbutton = self.selenium.find_element_by_css_selector('.createbutton button')
        self.assertFalse(createbutton.is_enabled())

        # Make sure the create button is clickable after both short and long names are entered.
        self._set_value('long_name', 'Test')
        self.assertFalse(createbutton.is_enabled())

        self._set_value('short_name', 'test')
        self.waitForEnabled(createbutton)

    #def test_success(self):
        #self.browseToTest('/@@create-new-assignment/1')
        #self.waitForCssSelector('.createnewassignmentform')

        #self._set_value('long_name', 'Test')
        #self._set_value('short_name', 'sometest')
        #createbutton = self.selenium.find_element_by_css_selector('.createbutton button')
        #self.waitForEnabled(createbutton)
        #createbutton.click()

        #self.waitForCssSelector('.createnewassignment-successpanel')
        #links = self.selenium.find_elements_by_css_selector('.actionlist a')
        #self.assertEquals(len(links), 2)
        #self.assertEquals(links[0].text, u'subjectadmin.createnewassignment.success.gotocreated')
        #self.assertEquals(links[0].get_attribute('href'), 'http://localhost:8000/subjectadmin/test#/duck1100/2012h/sometest/')
        #self.assertEquals(links[1].text, u'subjectadmin.createnewassignment.success.addanother')
        #self.assertEquals(links[1].get_attribute('href'), u'http://localhost:8000/subjectadmin/test#/@@create-new-assignment/1')

    #def test_success_direct(self):
        #self.browseToTest('/@@create-new-assignment/@@success')
        #self.waitForCssSelector('.x-message-box')
        #self.assertTrue('This page is only available after creating a new assignment.' in self.selenium.page_source)
