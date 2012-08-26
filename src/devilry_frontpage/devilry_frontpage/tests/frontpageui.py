from devilry.apps.core.testhelper import TestHelper
from .base import FrontpageSeleniumTestCase


def ui_datetimeformat(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

class TestFrontpageUI(FrontpageSeleniumTestCase):
    def setUp(self):
        self.fileinfo = {'ok.py': ['print ', 'meh']}
        self.testhelper = TestHelper()
        self.testhelper.create_user('student1')
        #self.testhelper.add(nodes='uni',
                            #subjects=['sub'],
                            #periods=['p1:begins(-3):ends(10)'], # -3months
                            #assignments=['a1:pub(1)', # 1 days after p1 begins
                                         #'a2:pub(30)']) # 30days after p1 begins

    def _get_absolute_url(self):
        return '{live_server_url}/'.format(live_server_url=self.live_server_url)

    def test_no_roles(self):
        self.login('student1')
        self.waitForCssSelector('.devilry_frontpage_overview')
        self.waitForCssSelector('.nopermissions')
        nopermtext = self.selenium.find_element_by_css_selector('.nopermissions').text.strip()
        self.assertTrue(nopermtext.startswith('You have no permissions on anything in Devilry.'))

    def test_always_visible_elements(self):
        self.login('student1')
        self.waitForCssSelector('.devilry_frontpage_overview')
        body = self.selenium.page_source
        self.assertTrue('Need help?' in body)
        self.assertTrue('Click on your name in the top right corner of the page.' in body)
        self.assertTrue('Improve Devilry?' in body)
        self.assertTrue('Choose your role' in body)

    def test_student(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-3):ends(10)'], # -3months
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.login('student1')
        self.waitForCssSelector('.devilry_frontpage_overview')
        frontpage = self.selenium.find_element_by_css_selector('.devilry_frontpage_overview')
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.student_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.examiner_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.administrator_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.superuser_role')), 0)

    def test_examiner(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-3):ends(10)'], # -3months
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.login('examiner1')
        self.waitForCssSelector('.devilry_frontpage_overview')
        frontpage = self.selenium.find_element_by_css_selector('.devilry_frontpage_overview')
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.student_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.examiner_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.administrator_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.superuser_role')), 0)

    def test_administrator(self):
        self.testhelper.add(nodes='uni:admin(admin1)')
        self.login('admin1')
        self.waitForCssSelector('.devilry_frontpage_overview')
        frontpage = self.selenium.find_element_by_css_selector('.devilry_frontpage_overview')
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.student_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.examiner_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.administrator_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.superuser_role')), 0)

    def test_superuser(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self.waitForCssSelector('.devilry_frontpage_overview')
        frontpage = self.selenium.find_element_by_css_selector('.devilry_frontpage_overview')
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.student_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.examiner_role')), 0)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.administrator_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.superuser_role')), 1)

    def test_allroles(self):
        self.testhelper.create_superuser('donald')
        self.testhelper.add(nodes='uni',
                            subjects=['sub:admin(donald)'],
                            periods=['p1:begins(-3):ends(10)'], # -3months
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(donald)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(donald)')
        self.login('donald')
        self.waitForCssSelector('.devilry_frontpage_overview')
        frontpage = self.selenium.find_element_by_css_selector('.devilry_frontpage_overview')
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.student_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.examiner_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.administrator_role')), 1)
        self.assertEquals(len(frontpage.find_elements_by_css_selector('.superuser_role')), 1)
