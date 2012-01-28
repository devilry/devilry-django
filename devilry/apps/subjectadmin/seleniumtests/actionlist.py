from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestShortcuts(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_actionlist(self):
        self.browseTo('/@@dashboard/actionlist')
        self.waitForCssSelector('.actionlist')
        self.assertTrue('Action list test' in self.driver.page_source)
        self.assertTrue('#/@@actionitem-1' in self.driver.page_source)
        self.assertTrue('#/@@actionitem-2' in self.driver.page_source)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Action item 1')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('Action item 2')), 1)
