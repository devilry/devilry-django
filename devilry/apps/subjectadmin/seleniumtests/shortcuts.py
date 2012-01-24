from devilry.apps.guibase.seleniumhelpers import SeleniumTestCase


class TestSelenium(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_shortcutlist(self):
        self.browseTo('/@@dashboard/shortcutlist')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('>2012h.assignment1<' in self.driver.page_source)
        self.assertTrue('>duck1100<' in self.driver.page_source)
        self.assertTrue('>week1<' in self.driver.page_source)
        self.assertTrue('href="#/duck-mek2030/2012h/assignment1"' in self.driver.page_source)

    def test_actionlist(self):
        self.browseTo('/@@dashboard/actionlist')
        self.waitForCssSelector('.actionlist')
        self.assertTrue('Action list test' in self.driver.page_source)
        self.assertTrue('#actionitem-1' in self.driver.page_source)
        self.assertTrue('#actionitem-2' in self.driver.page_source)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Action item 1')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Action item 2')), 1)

    def test_dashboard(self):
        self.browseTo('')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('Actions' in self.driver.page_source)
        self.assertTrue('#create-new-assignment' in self.driver.page_source)
        self.assertTrue('#browse-all' in self.driver.page_source)
        self.assertTrue('#register-for-final-exams' in self.driver.page_source)
        self.assertTrue('#global-statistics' in self.driver.page_source)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Create new assignment')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Browse all')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Register students that qualify for final exams')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Statistics')), 1)
