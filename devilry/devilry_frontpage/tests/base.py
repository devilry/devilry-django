import re
from seleniumhelpers import SeleniumTestCase
from django.test.utils import override_settings
from django.conf import settings


@override_settings(EXTJS4_DEBUG=False)
class FrontpageSeleniumTestCase(SeleniumTestCase):

    def browseTo(self, path):
        self.getPath('/devilry_student/#' + path)

    def login(self, username, password='test', redirect_to='/'):
        self.selenium.get('{0}{1}?next={2}'.format(self.live_server_url, settings.LOGIN_URL,
                                                   redirect_to))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
