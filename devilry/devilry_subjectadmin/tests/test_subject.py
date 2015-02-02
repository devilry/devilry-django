from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Subject

from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import RenameBasenodeTestMixin
from devilry.devilry_subjectadmin.tests.base import DeleteBasenodeTestMixin
from devilry.devilry_subjectadmin.tests.base import EditAdministratorsTestMixin


class TestSubjectListAll(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck1100:admin(duck1100adm)', 'duck1010:ln(DUCK 1010 - Programming)', 'duck9000'])
        self.url = '/allsubjects/'

    def _get_show_subject_url(self, subject):
        return '#/subject/{0}/'.format(subject.id)

    def test_listall(self):
        self.login('uniadmin')
        self.browseTo(self.url)
        self.waitForCssSelector('.devilry_allSubjectsList')
        self.assertTrue('All my subjects' in self.selenium.page_source)
        subjectlist = self.selenium.find_element_by_css_selector('.devilry_allSubjectsList')
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('li.devilry_subject')), 3)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1100')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck1010')), 1)
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('.devilry_subject_duck9000')), 1)
        self.assertTrue('DUCK 1010 - Programming' in self.selenium.page_source)
        self.assertTrue(self._get_show_subject_url(self.testhelper.duck1100) in self.selenium.page_source)
        self.assertTrue(self._get_show_subject_url(self.testhelper.duck1010) in self.selenium.page_source)
        self.assertTrue(self._get_show_subject_url(self.testhelper.duck9000) in self.selenium.page_source)

    def test_listall_limited(self):
        self.login('duck1100adm')
        self.browseTo(self.url)
        self.waitForCssSelector('.devilry_allSubjectsList')
        subjectlist = self.selenium.find_element_by_css_selector('.devilry_allSubjectsList')
        self.assertEquals(len(subjectlist.find_elements_by_css_selector('li.devilry_subject')), 1)


class SubjectTestCommonMixin(object):
    def browseToSubject(self, id):
        self.browseTo('/subject/{id}/'.format(id=id))


class TestSubjectOverview(SubjectAdminSeleniumTestCase, SubjectTestCommonMixin,
                          RenameBasenodeTestMixin, DeleteBasenodeTestMixin):
    renamebutton_id = 'subjectRenameButton'
    deletebutton_id = 'subjectDeleteButton'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin,anotheruniadmin)',
                            subjects=['duck1100:admin(duck1100adm)',
                                      'duck1010:ln(DUCK 1010 - Programming):admin(duck1010adm1,duck1010adm2,duck1010adm3)'])
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['period1:ln(Period One)', 'period2:ln(Period Two)', 'period3:ln(Period Three)'])
        self.testhelper.add(nodes='uni',
                            subjects=['duck1100'],
                            periods=['spring01:ln(Spring Year One)'])

    def _get_period_url(self, period):
        return '#/period/{0}/'.format(period.id)

    def test_doesnotexists(self):
        self.login('duck1010adm1')
        self.browseToSubject(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self.browseToSubject(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_list_of_periods(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        self.waitForText('DUCK 1010 - Programming')
        self.waitForCssSelector('li.devilry_period')
        periodlist = self.selenium.find_element_by_css_selector('.devilry_listofperiods')
        self.assertEquals(len(periodlist.find_elements_by_css_selector('li.devilry_period')), 3)
        self.assertTrue('Period One' in self.selenium.page_source)
        self.assertTrue('Period Two' in self.selenium.page_source)
        self.assertTrue('Period Three' in self.selenium.page_source)
        self.assertFalse('Spring Year One' in self.selenium.page_source)
        self.assertIn(self._get_period_url(self.testhelper.duck1010_period1), self.selenium.page_source)
        self.assertIn(self._get_period_url(self.testhelper.duck1010_period2), self.selenium.page_source)
        self.assertIn(self._get_period_url(self.testhelper.duck1010_period3), self.selenium.page_source)
        self.assertNotIn(self._get_period_url(self.testhelper.duck1100_spring01), self.selenium.page_source)

    def test_dangerous_panel(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        self.waitForText('Delete duck1010')
        self.waitForText('Rename duck1010')
        self.assertIn('Once you delete a subject, there is no going back', self.selenium.page_source)
        self.assertIn('Renaming a subject should not done without a certain amount of consideration', self.selenium.page_source)

    def test_rename(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        self.rename_test_helper(self.testhelper.duck1010)

    def test_rename_failure(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        self.rename_test_failure_helper()

    def test_delete(self):
        self.testhelper.add(nodes='uni',
                            subjects=['willbedeleted'])
        self.login('uniadmin')
        self.browseToSubject(self.testhelper.willbedeleted.id)
        delete_button = self.waitForAndFindElementByCssSelector('#subjectDeleteButton')
        self.assertTrue(delete_button.is_displayed())
        subjecturl = self.selenium.current_url
        self.perform_delete()
        self.waitFor(self.selenium, lambda s: s.current_url != subjecturl) # Will time out and fail unless the page is changed after delete
        self.assertEquals(Subject.objects.filter(id=self.testhelper.willbedeleted.id).count(), 0)

    def test_delete_notparentadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['willbedeleted:admin(willbedeletedadm)'])
        self.login('willbedeletedadm')
        self.browseToSubject(self.testhelper.willbedeleted.id)
        delete_button = self.waitForAndFindElementByCssSelector('#subjectDeleteButton')
        self.assertFalse(delete_button.is_displayed())

    def test_delete_not_empty(self):
        self.login('uniadmin')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        delete_button = self.waitForAndFindElementByCssSelector('#subjectDeleteButton')
        self.assertFalse(delete_button.is_displayed())

    def test_title(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectoverview')
        self.assertEquals(self.selenium.title, 'duck1010 - Devilry')

    def test_admins(self):
        self.testhelper.duck1010adm3.devilryuserprofile.full_name = 'Duck1010 admin three'
        self.testhelper.duck1010adm3.devilryuserprofile.save()
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectadmin_administratorlist')
        adminlist = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_administratorlist')
        self.assertEquals(len(adminlist.find_elements_by_css_selector('li')), 3)
        self.assertTrue('>duck1010adm1<' in self.selenium.page_source)
        self.assertTrue('>duck1010adm2<' in self.selenium.page_source)
        self.assertFalse('>duck1010adm3<' in self.selenium.page_source)
        self.assertTrue('Duck1010 admin three' in self.selenium.page_source)

    def test_inherited_admins(self):
        self.testhelper.uniadmin.devilryuserprofile.full_name = 'Uni admin'
        self.testhelper.uniadmin.devilryuserprofile.save()
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        self.waitForCssSelector('.devilry_subjectadmin_inherited_administratorlist')
        adminlist = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_inherited_administratorlist')
        self.assertEquals(len(adminlist.find_elements_by_css_selector('li')), 2)
        self.assertTrue('>anotheruniadmin<' in self.selenium.page_source)
        self.assertFalse('>uniadmin<' in self.selenium.page_source)
        self.waitForCssSelector('.devilry_subjectadmin_inherited_administratorlist .inherited_administratorlistitem_uniadmin')
        self.assertTrue('Uni admin' in self.selenium.page_source)

    def test_breadcrumb(self):
        self.login('duck1010adm1')
        self.browseToSubject(self.testhelper.duck1010.id)
        breadcrumbtext = self.get_breadcrumbstring('duck1010')
        self.assertEquals(breadcrumbtext, ['All my subjects', 'duck1010'])


class TestSubjectEditAdministrators(SubjectAdminSeleniumTestCase,
                                    EditAdministratorsTestMixin,
                                    SubjectTestCommonMixin):

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck1100'])
        self.login('uniadmin')

    def getBasenode(self):
        return self.testhelper.duck1100

    def browseToTestBasenode(self):
        self.browseToSubject(self.testhelper.duck1100.id)
