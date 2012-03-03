from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestShortcuts(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_shortcutlist(self):
        self.browseToTest('/@@dashboard/shortcutlist')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('>duck1100<' in self.driver.page_source)
        self.assertTrue('>Week one<' in self.driver.page_source)
        self.assertTrue('>2012h.Assignment one<' in self.driver.page_source)
        self.assertTrue('href="#/duck-mek2030/2012h/assignment1"' in self.driver.page_source)
