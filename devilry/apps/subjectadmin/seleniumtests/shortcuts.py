from devilry.apps.guibase.seleniumhelpers import SeleniumTestCase


class TestSelenium(SeleniumTestCase):
    appname = 'subjectadmin'
    def test_list_populated(self):
        self.assertEquals(self.driver.title, 'Devilry')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('>2012h.assignment1<' in self.driver.page_source)
        self.assertTrue('>duck1100<' in self.driver.page_source)
        self.assertTrue('>week1<' in self.driver.page_source)
        #print dir(self.driver.find_element_by_css_selector(".shortcutlist>ul"))
