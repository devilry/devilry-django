from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestAssignment(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
        self.browseToTest('/a/b/c') # This is not a valid path to an assignment
        self.waitForCssSelector('.assignment')
        self.waitForCssSelector('.messagemask')
        self.assertTrue('themebase.doesnotexist' in self.driver.page_source)
        self.assertTrue('a.b.c' in self.driver.page_source)

    def test_shortcuts_render(self):
        self.browseToTest('/duck1100/2012h/week2') # This is not a valid path to an assignment
        self.waitForCssSelector('.assignment')
        self.assertTrue('themebase.edit-something' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.manage-students' in self.driver.page_source)
        self.assertTrue('subjectadmin.assignment.manage-deadlines' in self.driver.page_source)
        self.assertTrue('themebase.delete-something' in self.driver.page_source)
