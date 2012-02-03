from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestAssignment(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
        self.browseToTest('/a/b/c') # This is not a valid path to an assignment
        self.waitForCssSelector('.assignmentoverview')
        self.waitForCssSelector('.messagemask')
        self.assertTrue('themebase.doesnotexist' in self.driver.page_source)
        self.assertTrue('a.b.c' in self.driver.page_source)

    def test_shortcuts_render(self):
        self.browseToTest('/duck1100/2012h/week2')
        self.waitForCssSelector('.assignmentoverview')
        self.assertTrue('subjectadmin.assignment.manage-students' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.manage-deadlines' in self.driver.page_source)
        self.assertTrue('themebase.delete-something' in self.driver.page_source)

    def test_notpublished(self):
        self.browseToTest('/duck1100/2012h/week2') # Set to nextmonth in AssignmentTestMock
        self.waitForText('subjectadmin.assignment.notpublished.title')
        self.assertTrue('subjectadmin.assignment.notpublished.body' in self.driver.page_source)

    def test_published(self):
        self.browseToTest('/duck1100/2012h/week1') # Set to yesterday in AssignmentTestMock
        self.waitForText('subjectadmin.assignment.published.title')
        self.assertTrue('subjectadmin.assignment.published.body' in self.driver.page_source)



class TestEditPublishingTime(SeleniumTestCase):
    appname = 'subjectadmin'

    def afterSetUp(self):
        self.browseToTest('/duck1100/2012h/week1') # Set to yesterday in AssignmentTestMock
        self.waitForCssSelector('.publishingtime-editablesidebarbox button')
        button = self.driver.find_element_by_css_selector('.publishingtime-editablesidebarbox button')
        button.click()
        self.waitForCssSelector('.editpublishingtime')

        editpublishingtime_window = self.driver.find_element_by_css_selector('.editpublishingtime')
        self.datefield = editpublishingtime_window.find_element_by_css_selector('.themebase-datefield input')
        self.timefield = editpublishingtime_window.find_element_by_css_selector('.themebase-timefield input')
        self.savebutton = editpublishingtime_window.find_element_by_css_selector('.savebutton button')

    def _set_datetime(self, date, time):
        self.datefield.clear()
        self.timefield.clear()
        self.datefield.send_keys(date)
        self.timefield.send_keys(time)

    def test_editpublishingtime(self):
        self.assertTrue('subjectadmin.assignment.editpublishingtime.title' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.editpublishingtime.help' in self.driver.page_source)
        self._set_datetime('2012-02-15', '12:00')
        self.savebutton.click()
        self.waitForText('2012-02-15T12:00') # If this times out, the proxy has not been updated

    def test_editpublishingtime_errorhandling(self):
        self._set_datetime('2012-02-01', '12:00') # subjectadmin.model.AssignmentTestMock defines day 01 to raise an error (for _this_ testcase)
        self.savebutton.click()
        self.waitForText('It is triggered since the day of month is "1" (for testing only).') # If this times out, the error was not added to the body
