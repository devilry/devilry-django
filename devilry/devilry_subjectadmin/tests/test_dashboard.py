from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder, SubjectBuilder, NodeBuilder


class TestDashboard(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def test_dashboard_list_active(self):
        NodeBuilder('ducku')\
            .add_subject(short_name='duck1010', long_name='DUCK 1010 Programming')\
            .add_admins(self.testuser)\
            .add_6month_active_period()

        self.loginTo('testuser', path='')
        self.waitForCssSelector('.devilry_subjectadmin_allactivewhereisadminlist')
        self.assertIn('Active subjects', self.selenium.page_source)
        self.assertIn('DUCK 1010 Programming', self.selenium.page_source)

        browse_all_button = self.selenium.find_element_by_link_text(
            'Browse everything where you are administrator')
        self.assertEquals(browse_all_button.get_attribute('href'),
                          self.get_absolute_url('/'))

    def test_dashboard_list_exclude_inactive(self):
        NodeBuilder('ducku')\
            .add_subject(short_name='duck1010', long_name='DUCK 1010 Programming')\
            .add_admins(self.testuser)\
            .add_6month_lastyear_period()

        self.loginTo('testuser', path='')
        self.waitForCssSelector('.devilry_subjectadmin_allactivewhereisadminlist')
        self.assertIn('Active subjects', self.selenium.page_source)
        self.assertNotIn('DUCK 1010 Programming', self.selenium.page_source)

        browse_all_button = self.selenium.find_element_by_link_text(
            'Browse everything where you are administrator')
        self.assertEquals(browse_all_button.get_attribute('href'),
                          self.get_absolute_url('/'))
