from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestSubjectListAll(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
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
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('500: Server error' in self.driver.page_source)

    def test_published(self):
        self.browseToTest('/')
        self.waitForText('core.subject.plural')
        self.assertTrue('DUCK 1100 - Introduction to Python programming' in self.driver.page_source)
        self.assertTrue('DUCK-MEK 2030 - Something Mechanical' in self.driver.page_source)
