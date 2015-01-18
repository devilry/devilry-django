import unittest
from devilry.apps.core.testhelper import TestHelper

from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase



class RelatedUsersUITestMixin(object):
    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_relatedusers {0}'.format(cssselector))
    def find_elements(self, cssselector):
        return self.selenium.find_elements_by_css_selector('.devilry_subjectadmin_relatedusers {0}'.format(cssselector))

    def waitForGridRowCount(self, count):
        self.waitFor(self.selenium, lambda s: len(self.find_gridrows()) == count)

    def find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_relatedusergrid .x-grid-row')

    def get_row_by_username(self, username):
        cssselector = '.relateduser_username_{username}'.format(username=username)
        self.waitForCssSelector('.x-grid-row {0}'.format(cssselector))
        for row in self.find_gridrows():
            matches = row.find_elements_by_css_selector(cssselector)
            if len(matches) > 0:
                return row
        raise ValueError('Could not find any rows matching the following username: {0}.'.format(username))

    def click_row_by_username(self, username, add_to_selection=True):
        self.get_row_by_username(username).find_element_by_css_selector('.x-grid-row-checker').click()

    def get_row_data(self, row):
        result = {}
        result['full_name'] = row.find_element_by_css_selector('.meta_cell .full_name').text.strip()
        result['username'] = row.find_element_by_css_selector('.meta_cell .username').text.strip()
        result['tags'] = row.find_element_by_css_selector('.tags_cell').text.strip()
        return result

    def click_add_related_user_button(self):
        self.waitForCssSelector('.add_related_user_button')
        addbutton = self.find_element('.add_related_user_button')
        addbutton.click()

    def ui_add_related_user(self, username):
        usersearchfield = self.find_element('.devilry_subjectadmin_selectrelateduserpanel input[type=text]')
        self.click_add_related_user_button()
        self.waitForDisplayed(usersearchfield)
        usersearchfield.send_keys(username)
        match = self.waitForAndFindElementByCssSelector('.autocompleteuserwidget_matchlist .matchlistitem_{0}'.format(username))
        match.click()
        self.waitForNotDisplayed(usersearchfield)
        self.waitForCssSelector('.alert-success')
        user = getattr(self.testhelper, username)
        displayname = user.devilryuserprofile.full_name or user.username
        self.waitForText('{0} added'.format(displayname))

    def click_remove_button(self):
        removebutton = self.waitForAndFindElementByCssSelector('.remove_related_user_button button')
        removebutton.click()

    def ui_remove_related_users(self, *usernames):
        displaynames = []
        for username in usernames:
            self.click_row_by_username(username)
            user = getattr(self.testhelper, username)
            displayname = user.devilryuserprofile.full_name or user.username
            displaynames = []
        self.click_remove_button()
        removeconfirmbutton = self.find_element('.removeconfirmpanel .okbutton button')
        self.waitForDisplayed(removeconfirmbutton)
        removeconfirmbutton.click()
        self.waitForText('Removed: {0}'.format(', '.join(displaynames)))

    def click_tagbutton(self, action):
        tagsbutton = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_relatedusers .related_users_tags_button')
        tagsbutton.click()
        cssselector = '.{0}_tags_button'.format(action)
        button = self.waitForAndFindElementByCssSelector(cssselector)
        self.waitForDisplayed(button)
        button.click()
        cssselector = '.devilry_subjectadmin_relatedusers .{0}_tags_panel'.format(action)
        panel = self.waitForAndFindElementByCssSelector(cssselector)
        self.waitForDisplayed(panel)
        return panel

    def ui_set_or_add_tags(self, action, tags):
        panel = self.click_tagbutton(action)
        textarea = panel.find_element_by_css_selector('textarea')
        textarea.send_keys(','.join(tags))
        savebutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitForEnabled(savebutton)
        savebutton.click()
        self.waitForCssSelector('.alert-success')
        self.waitForText('with: {0}'.format(', '.join(tags)))

    def ui_set_or_add_tags_cancel(self, action):
        panel = self.click_tagbutton(action)
        cancelbutton = panel.find_element_by_css_selector('.choosetags_cancelbutton button')
        self.waitForEnabled(cancelbutton)
        cancelbutton.click()
        helpbox = self.getHelpBox()
        self.waitForDisplayed(helpbox)

    def ui_clear_tags(self):
        panel = self.click_tagbutton('clear')
        okbutton = panel.find_element_by_css_selector('.okbutton')
        self.waitForDisplayed(okbutton)
        okbutton.click()
        self.waitForCssSelector('.alert-success')
        self.waitForText('Cleared tags on')

    def getHelpBox(self):
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_relatedusers .related_user_helpbox')


class TestRelatedStudentsUI(SubjectAdminSeleniumTestCase, RelatedUsersUITestMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'])
        self.period = self.testhelper.sub_p1

    def _browseToManageStudentsAs(self, username, period_id):
        path = '/period/{0}/@@relatedstudents'.format(period_id)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_relatedstudents')


    def _add_relatedstudent(self, username, full_name=None, tags='', candidate_id=None):
        user = self.testhelper.create_user(username, fullname=full_name)
        self.period.relatedstudent_set.create(user=user,
                                              tags=tags,
                                              candidate_id=candidate_id)

    def test_render(self):
        self._add_relatedstudent('student1', full_name='Student One',
                                 tags='a,b',
                                 candidate_id='SEC-RET')
        self._add_relatedstudent('student2')
        self._add_relatedstudent('student3', full_name='Student Three')
        self._browseToManageStudentsAs('p1admin', self.period.id)

        self.waitForCssSelector('.devilry_subjectadmin_relatedusers')
        self.waitForGridRowCount(3)
        self.assertEquals(self.get_row_data(self.get_row_by_username('student1')),
                          {'full_name': 'Student One',
                           'username': 'student1',
                           'tags': 'a,b'})
        self.assertEquals(self.get_row_data(self.get_row_by_username('student2')),
                          {'full_name': 'Full name missing',
                           'username': 'student2',
                           'tags': ''})
        self.assertEquals(self.get_row_data(self.get_row_by_username('student3')),
                          {'full_name': 'Student Three',
                           'username': 'student3',
                           'tags': ''})

    def test_invalid_period_id(self):
        self._browseToManageStudentsAs('p1admin', 1000000)
        def find_permissiondeniedmessage(s):
            for message in self.selenium.find_elements_by_css_selector('.devilry_extjsextras_alertmessage'):
                if 'Permission denied' in message.text.strip():
                    return True
            return False
        self.waitFor(self.selenium, find_permissiondeniedmessage)

    def test_add_student(self):
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')
        self.testhelper.create_user('student1')
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student1').exists())

        self.ui_add_related_user('student1')
        self.waitForGridRowCount(1)
        self.assertTrue(self.period.relatedstudent_set.filter(user__username='student1').exists())

    def test_add_student_cancel(self):
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')
        self.testhelper.create_user('student1')
        self.ui_add_related_user('student1')
        self.click_add_related_user_button()
        cancelbutton = self.find_element('.devilry_subjectadmin_selectrelateduserpanel .cancelbutton button')
        self.waitForDisplayed(cancelbutton)
        cancelbutton.click()
        self.waitForNotDisplayed(cancelbutton)

    def test_remove_single(self):
        self._add_relatedstudent('student1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_relatedusers')
        self.waitForGridRowCount(1)
        self.ui_remove_related_users('student1')
        self.waitForGridRowCount(0)
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student1').exists())

    @unittest.skip('See https://github.com/devilry/devilry-django/issues/651')
    def test_remove_many(self):
        self._add_relatedstudent('student1')
        self._add_relatedstudent('student2', full_name='Student Two')
        self._add_relatedstudent('student3', full_name='Student Three')
        self._add_relatedstudent('ignored', full_name='Ignored student')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_relatedusers')
        self.waitForGridRowCount(4)
        self.ui_remove_related_users('student1', 'student2', 'student3')
        self.waitForGridRowCount(1)
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student1').exists())
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student2').exists())
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student3').exists())
        self.assertTrue(self.period.relatedstudent_set.filter(user__username='ignored').exists())

    def test_remove_enable_disable(self):
        self._add_relatedstudent('student1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        removebutton = self.waitForAndFindElementByCssSelector('.remove_related_user_button button')
        self.assertFalse(removebutton.is_enabled())
        self.click_row_by_username('student1')
        self.waitForEnabled(removebutton)
        self.click_row_by_username('student1')
        self.waitForDisabled(removebutton)

    def test_add_tags(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='a,b')
        self._add_relatedstudent('ignored', tags='unchanged')
        self._browseToManageStudentsAs('p1admin', self.period.id)

        self.click_row_by_username('student1')
        self.click_row_by_username('student2')
        self.ui_set_or_add_tags('add', ['bad', 'supergood', 'awesome'])

        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          'good,bad,supergood,awesome')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          'a,b,bad,supergood,awesome')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='ignored').tags,
                          'unchanged')

    def test_add_tags_cancel(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='group1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.click_row_by_username('student1')
        self.click_row_by_username('student2')
        self.ui_set_or_add_tags_cancel('add')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          'good,bad')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          'group1')

    def test_set_tags(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='a,b')
        self._add_relatedstudent('ignored', tags='unchanged')
        self._browseToManageStudentsAs('p1admin', self.period.id)

        self.click_row_by_username('student1')
        self.click_row_by_username('student2')
        self.ui_set_or_add_tags('set', ['bad', 'supergood', 'awesome'])

        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          'bad,supergood,awesome')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          'bad,supergood,awesome')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='ignored').tags,
                          'unchanged')

    def test_set_tags_cancel(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='group1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.click_row_by_username('student1')
        self.click_row_by_username('student2')
        self.ui_set_or_add_tags_cancel('set')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          'good,bad')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          'group1')


    def test_clear_tags(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='group1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.click_row_by_username('student1')
        self.click_row_by_username('student2')
        self.ui_clear_tags()
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          '')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          '')

    def test_clear_tags_cancel(self):
        self._add_relatedstudent('student1', tags='good,bad')
        self._add_relatedstudent('student2', tags='group1')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.click_row_by_username('student1')
        self.click_row_by_username('student2')

        panel = self.click_tagbutton('clear')
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton')
        self.waitForDisplayed(cancelbutton)
        cancelbutton.click()

        helpbox = self.getHelpBox()
        self.waitForDisplayed(helpbox)

        self.assertEquals(self.period.relatedstudent_set.get(user__username='student1').tags,
                          'good,bad')
        self.assertEquals(self.period.relatedstudent_set.get(user__username='student2').tags,
                          'group1')
