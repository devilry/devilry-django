from devilry.apps.guibase.seleniumhelpers import SeleniumTestCase


class TestDashboard(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_dashboard(self):
        self.browseTo('')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('Actions' in self.driver.page_source)
        self.assertTrue('#/@@create-new-assignment/@@chooseperiod' in self.driver.page_source)
        self.assertTrue('href="#/"' in self.driver.page_source)
        self.assertTrue('#/@@register-for-final-exams' in self.driver.page_source)
        self.assertTrue('#/@@global-statistics' in self.driver.page_source)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Create new assignment')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Browse all')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Register students that qualify for final exams')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Statistics')), 1)
