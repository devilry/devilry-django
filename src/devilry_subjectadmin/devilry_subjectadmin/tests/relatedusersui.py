from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



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
        for row in self.find_gridrows():
            matches = row.find_elements_by_css_selector('.relateduser_username_{username}'.format(username=username))
            if len(matches) > 0:
                return row
        raise ValueError('Could not find any rows matching the following username: {0}.'.format(username))

    def click_row_by_username(self, username):
        self.get_row_by_username(username).click()

    def get_row_data(self, row):
        result = {}
        result['full_name'] = row.find_element_by_css_selector('.meta_cell .full_name').text.strip()
        result['username'] = row.find_element_by_css_selector('.meta_cell .username').text.strip()
        result['tags'] = row.find_element_by_css_selector('.tags_cell').text.strip()
        candidate_id_elements = row.find_elements_by_css_selector('.meta_cell .candidate_id')
        if len(candidate_id_elements) == 1:
            result['candidate_id'] = candidate_id_elements[0].text.strip()
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


class TestRelatedStudentsUI(SubjectAdminSeleniumTestCase, RelatedUsersUITestMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'])
        self.period = self.testhelper.sub_p1

    def _browseToManageStudentsAs(self, username, period_id):
        path = '/period/{0}/@@related-students'.format(period_id)
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

        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')
        self.waitForGridRowCount(3)
        self.assertEquals(self.get_row_data(self.get_row_by_username('student1')),
                          {'full_name': 'Student One',
                           'username': 'student1',
                           'tags': 'a,b',
                           'candidate_id': 'SEC-RET'})
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
        # Should get one error for Period, and one for relatedusers
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.devilry_extjsextras_alertmessage')) == 2)
        for message in self.find_elements('.devilry_extjsextras_alertmessage'):
            self.assertIn('403', message.text.strip())

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
        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')
        self.waitForGridRowCount(1)
        self.ui_remove_related_users('student1')
        self.waitForGridRowCount(0)
        self.assertFalse(self.period.relatedstudent_set.filter(user__username='student1').exists())

    def test_remove_many(self):
        self._add_relatedstudent('student1')
        self._add_relatedstudent('student2', full_name='Student Two')
        self._add_relatedstudent('student3', full_name='Student Three')
        self._add_relatedstudent('ignored', full_name='Ignored student')
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')
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
