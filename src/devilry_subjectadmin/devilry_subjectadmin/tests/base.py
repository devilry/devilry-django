from seleniumhelpers import SeleniumTestCase
from django.test.utils import override_settings
from django.conf import settings


@override_settings(EXTJS4_DEBUG=False)
class SubjectAdminSeleniumTestCase(SeleniumTestCase):
    def browseTo(self, path):
        self.getPath('/devilry_subjectadmin/#' + path)

    def login(self, username, password='test'):
        self.selenium.get('%s%s' % (self.live_server_url, settings.LOGIN_URL))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
