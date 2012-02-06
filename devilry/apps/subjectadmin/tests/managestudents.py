from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestManageStudents(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
        self.browseToTest('/a/b/c/@@manage-students') # This is not a valid path to an assignment
        self.waitForCssSelector('.managestudentsoverview')
        self.waitForCssSelector('.messagemask')
        self.assertTrue('themebase.doesnotexist' in self.driver.page_source)
        self.assertTrue('a.b.c' in self.driver.page_source)

    def test_load_relatedstudents(self):
        self.browseToTest('/duck1100/2012h/week1/@@manage-students')
        self.waitForCssSelector('.all-items-loaded')
        self.waitForCssSelector('#relatedstudentproxy .hiddenelement-text')
        proxytext = self.driver.find_element_by_css_selector('#relatedstudentproxy .hiddenelement-text')
        self.waitFor(proxytext, lambda element: len(element.text) > 0)
        self.assertTrue('"candidate_id": "secretcand0"' in proxytext.text)
        self.assertTrue('"candidate_id": "secretcand2"' in proxytext.text)
