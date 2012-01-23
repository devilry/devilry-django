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
