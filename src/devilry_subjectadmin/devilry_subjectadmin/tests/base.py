import re
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

    def get_absolute_url(self, path):
        return '{live_server_url}/devilry_subjectadmin/#{path}'.format(live_server_url=self.live_server_url,
                                                                       path=path)
    def get_breadcrumbstring(self, expected_contains):
        self.waitForCssSelector('.devilry_extjsextras_breadcrumb')
        def breadcrumbLoaded(breadcrumb):
            return expected_contains in breadcrumb.text
        breadcrumb = self.selenium.find_element_by_css_selector('.devilry_extjsextras_breadcrumb')
        self.waitFor(breadcrumb, breadcrumbLoaded)
        return re.split('\s*\/\s*', breadcrumb.text)


class RenameBasenodeTestMixin(object):
    renamebutton_id = None

    def _get_field(self, containercls, fieldname):
        field = self.selenium.find_element_by_css_selector('{0} input[name={1}]'.format(containercls, fieldname))
        return field

    def _init_renametest(self):
        self.selenium.find_element_by_css_selector('#{0} button'.format(self.renamebutton_id)).click()
        self.waitForCssSelector('.devilry_rename_basenode_window')
        window = self.selenium.find_element_by_css_selector('.devilry_rename_basenode_window')
        short_name = self._get_field('.devilry_rename_basenode_window', 'short_name')
        long_name = self._get_field('.devilry_rename_basenode_window', 'long_name')
        savebutton = window.find_element_by_css_selector('.devilry_extjsextras_savebutton button')
        return window, short_name, long_name, savebutton

    def rename_test_helper(self, basenode):
        window, short_name, long_name, savebutton = self._init_renametest()
        self.assertEquals(short_name.get_attribute('value'), basenode.short_name)
        self.assertEquals(long_name.get_attribute('value'), basenode.long_name)

        short_name.clear()
        self.waitForDisabled(savebutton)
        short_name.send_keys('renamed-shortname')
        long_name.clear()
        self.waitForDisabled(savebutton)
        long_name.send_keys('Renamed long name')
        self.waitForEnabled(savebutton)

        savebutton.click()
        self.waitForTitleContains('renamed-shortname')
        updated = basenode.__class__.objects.get(id=basenode.id)
        self.assertEquals(updated.short_name, 'renamed-shortname')
        self.assertEquals(updated.long_name, 'Renamed long name')

    def rename_test_failure_helper(self):
        window, short_name, long_name, savebutton = self._init_renametest()
        short_name.clear()
        short_name.send_keys('Renamed-shortname')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.devilry_extjsextras_alertmessagelist .alert-error')), 0)
        savebutton.click()
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist', within=window)
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.devilry_extjsextras_alertmessagelist .alert-error')), 1)

class DeleteBasenodeTestMixin(object):
    deletebutton_id = None

    def click_delete_button(self):
        self.selenium.find_element_by_css_selector('#{0} button'.format(self.deletebutton_id)).click()

    def perform_delete(self):
        self.click_delete_button()
        self.waitForCssSelector('.devilry_confirmdeletedialog')
        window = self.selenium.find_element_by_css_selector('.devilry_confirmdeletedialog')
        inputfield = self._get_field('.devilry_confirmdeletedialog', 'confirm_text')
        deletebutton = window.find_element_by_css_selector('.devilry_deletebutton button')
        inputfield.send_keys('DELETE')
        self.waitForEnabled(deletebutton)
        deletebutton.click()
