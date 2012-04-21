from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase



class TestPeriodOverview(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_servererror(self):
        self.browseToTest('/duck-mek2030/2012h/', query='servererror=1') # subjectadmin.store.PeriodsTestMock simulates servererror with this querystring
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('500: Server error' in self.driver.page_source)

    def test_doesnotexists(self):
        self.browseToTest('/duck-mek2030/doesnotexist/')
        self.waitForCssSelector('.periodoverview')
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('400: Error' in self.driver.page_source)

    def test_published(self):
        self.browseToTest('/duck-mek2030/2012h-extra/')
        self.waitForCssSelector('.periodoverview')
        self.waitForCssSelector('.listofassignments')
        self.assertTrue('>Extra superhard assignment' in self.driver.page_source)
        self.assertTrue('subjectadmin.administrators' in self.driver.page_source)
        self.assertTrue('#/duck-mek2030/2012h-extra/extra/' in self.driver.page_source)
