import re
from seleniumhelpers import SeleniumTestCase
from django.test.utils import override_settings
from django.conf import settings


@override_settings(EXTJS4_DEBUG=False)
class StudentSeleniumTestCase(SeleniumTestCase):

    def browseTo(self, path):
        self.getPath('/devilry_student/#' + path)

    def login(self, username, password='test'):
        self.selenium.get('{0}{1}?next=/devilry_student/emptytestview'.format(self.live_server_url, settings.LOGIN_URL))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def get_absolute_url(self, path):
        return '{live_server_url}/devilry_student/#{path}'.format(live_server_url=self.live_server_url,
                                                                  path=path)
    def get_breadcrumbstring(self, expected_contains):
        self.waitForCssSelector('.devilry_header_breadcrumb')
        def breadcrumbLoaded(breadcrumb):
            return expected_contains in breadcrumb.text
        breadcrumb = self.selenium.find_element_by_css_selector('.devilry_header_breadcrumb')
        self.waitFor(breadcrumb, breadcrumbLoaded)
        default_breadcrumb = 'Dashboard'
        breadcrumbtext = breadcrumb.text
        if breadcrumb.text.startswith(default_breadcrumb):
            breadcrumbtext = breadcrumbtext[len(default_breadcrumb)+1:]
        return re.split('\s*\/\s*', breadcrumbtext)
