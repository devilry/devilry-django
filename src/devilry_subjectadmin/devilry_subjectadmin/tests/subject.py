from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


class TestSubjectListAll(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck1100:admin(duck1100adm)', 'duck1010:ln(DUCK 1010 - Programming)', 'duck9000'])

    def _geturl(self, subject):
        return '#/{0}/'.format(subject.id)

    def test_listall(self):
        self.login('uniadmin')
        self.browseTo('/')
        self.waitForCssSelector('.devilry_allSubjectsList')
        self.assertTrue('All subjects' in self.selenium.page_source)
        subjectlist = self.selenium.find_element_by_css_selector('.devilry_allSubjectsList')
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('li.devilry_subject')), 3)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1100')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1010')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck9000')), 1)
        self.assertTrue('DUCK 1010 - Programming' in self.selenium.page_source)
        self.assertTrue(self._geturl(self.testhelper.duck1100) in self.selenium.page_source)
        self.assertTrue(self._geturl(self.testhelper.duck1010) in self.selenium.page_source)
        self.assertTrue(self._geturl(self.testhelper.duck9000) in self.selenium.page_source)

    def test_listall_limited(self):
        self.login('duck1100adm')
        self.browseTo('/')
        self.waitForCssSelector('.devilry_allSubjectsList')
        subjectlist = self.selenium.find_element_by_css_selector('.devilry_allSubjectsList')
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('li.devilry_subject')), 1)


class TestSubjectOverview(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck1100:admin(duck1100adm)',
                                      'duck1010:ln(DUCK 1010 - Programming):admin(duck1010adm)'])
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['period1:ln(Period One)', 'period2', 'period3'])
        self.testhelper.add(nodes='uni',
                            subjects=['duck1100'],
                            periods=['spring01'])

    def test_doesnotexists(self):
        self.login('duck1010adm')
        self.browseTo('/100000/')
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self.browseTo('/100000/')
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_published(self):
        self.login('duck1010adm')
        self.browseTo('/{0}/'.format(self.testhelper.duck1010.id))
        self.waitForCssSelector('.devilry_subjectoverview')
        self.waitForText('DUCK 1010 - Programming')
        self.waitForCssSelector('li.devilry_period')
        periodlist = self.selenium.find_element_by_css_selector('.devilry_listofperiods')
        self.assertEquals(len(periodlist.find_elements_by_css_selector('li.devilry_period')), 3)
        self.assertTrue('Period One' in self.selenium.page_source)
        self.assertTrue('period2' in self.selenium.page_source)
        self.assertTrue('period3' in self.selenium.page_source)
        self.assertFalse('spring01' in self.selenium.page_source)
