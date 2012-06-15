from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


class TestSubjectListAll(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self.testhelper.add(nodes='uni',
                            subjects=['duck1100', 'duck1010:ln(DUCK 1010 - Programming)', 'duck9000'])

    #def test_servererror(self):
        #self.browseToTest('/', query='servererror=1') # subjectadmin.store.SubjectsTestMock simulates servererror with this querystring
        #self.waitForCssSelector('.alertmessagelist')
        #self.assertTrue('500: Server error' in self.selenium.page_source)

    def test_published(self):
        self.browseTo('/')
        self.waitForCssSelector('.devilry_allSubjectsList')
        self.assertTrue('All subjects' in self.selenium.page_source)
        subjectlist = self.selenium.find_element_by_css_selector('.devilry_allSubjectsList')
        #raw_input('ENTER')
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('li.devilry_subject')), 3)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1100')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1010')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck9000')), 1)
        self.assertTrue('DUCK 1010 - Programming' in self.selenium.page_source)
        self.assertTrue('#/duck1100/' in self.selenium.page_source)
        self.assertTrue('#/duck1010/' in self.selenium.page_source)
        self.assertTrue('#/duck9000/' in self.selenium.page_source)


#class TestSubjectOverview(SeleniumTestCase):
    #appname = 'subjectadmin'

    #def test_doesnotexists(self):
        #self.browseToTest('/a/')
        #self.waitForCssSelector('.subjectoverview')
        #self.waitForCssSelector('.alertmessagelist')
        #self.assertTrue('400: Error' in self.selenium.page_source)

    #def test_published(self):
        #self.browseToTest('/duck-mek2030/')
        #self.waitForCssSelector('.subjectoverview')
        #self.waitForText('DUCK-MEK 2030 - Something Mechanical')
        #self.assertTrue('>Spring 2012 extra assignments<' in self.selenium.page_source)
        #self.assertTrue('>Spring 2012<' in self.selenium.page_source)
        #self.assertTrue('subjectadmin.administrators' in self.selenium.page_source)
        #self.assertTrue('#/duck-mek2030/2012h-extra/' in self.selenium.page_source)
        #self.assertTrue('#/duck-mek2030/2012h/' in self.selenium.page_source)
