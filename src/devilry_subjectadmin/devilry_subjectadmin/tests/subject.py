from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestSubjectListAll(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_servererror(self):
        self.browseToTest('/', query='servererror=1') # subjectadmin.store.SubjectsTestMock simulates servererror with this querystring
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('500: Server error' in self.driver.page_source)

    def test_published(self):
        self.browseToTest('/')
        self.waitForText('core.subject.plural')
        self.assertTrue('DUCK 1100 - Introduction to Python programming' in self.driver.page_source)
        self.assertTrue('DUCK-MEK 2030 - Something Mechanical' in self.driver.page_source)


class TestSubjectOverview(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
        self.browseToTest('/a/')
        self.waitForCssSelector('.subjectoverview')
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('400: Error' in self.driver.page_source)

    def test_published(self):
        self.browseToTest('/duck-mek2030/')
        self.waitForCssSelector('.subjectoverview')
        self.waitForText('DUCK-MEK 2030 - Something Mechanical')
        self.assertTrue('>Spring 2012 extra assignments<' in self.driver.page_source)
        self.assertTrue('>Spring 2012<' in self.driver.page_source)
        self.assertTrue('subjectadmin.administrators' in self.driver.page_source)
        self.assertTrue('#/duck-mek2030/2012h-extra/' in self.driver.page_source)
        self.assertTrue('#/duck-mek2030/2012h/' in self.driver.page_source)
