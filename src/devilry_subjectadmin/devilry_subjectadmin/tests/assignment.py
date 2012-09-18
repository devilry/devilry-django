from datetime import datetime, timedelta
from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase
from .base import RenameBasenodeTestMixin
from .base import DeleteBasenodeTestMixin



class TestAssignment(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _loginToAssignment(self, username, id):
        self.loginTo(username, '/assignment/{id}/'.format(id=id))

    def test_doesnotexists(self):
        self.testhelper.create_user('normal')
        self._loginToAssignment('normal', 100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self._loginToAssignment('grandma', 100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_shortcuts_render(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.assertTrue('Manage students' in self.selenium.page_source)
        self.assertTrue('Manage deadlines' in self.selenium.page_source)

    def test_title(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.waitFor(self.selenium, lambda s: s.title == 'sub.period1.week2 - Devilry')

    def test_notpublished(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime_widget .editablesidebarbox_body .danger')

    def test_published(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2)'],
                            assignments=['week2:admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime_widget .editablesidebarbox_body .success')


class TestAssignmentDangerous(SubjectAdminSeleniumTestCase, RenameBasenodeTestMixin, DeleteBasenodeTestMixin):
    renamebutton_id = 'assignmentRenameButton'
    deletebutton_id = 'assignmentDeleteButton'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['sub'],
                            periods=['period1:begins(-2):admin(p1admin)'],
                            assignments=['week1:admin(weekadmin)'])

    def _loginToAssignment(self, username, id):
        self.loginTo(username, '/assignment/{id}/'.format(id=id))

    def test_rename(self):
        self._loginToAssignment('weekadmin', self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.rename_test_helper(self.testhelper.sub_period1_week1)

    def test_rename_failure(self):
        self._loginToAssignment('weekadmin', self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.rename_test_failure_helper()

    def test_delete(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2):admin(p1admin)'],
                            assignments=['willbedeleted'])
        self._loginToAssignment('p1admin', self.testhelper.sub_period1_willbedeleted.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        assignmenturl = self.selenium.current_url
        self.perform_delete()
        self.waitFor(self.selenium, lambda s: s.current_url != assignmenturl) # Will time out and fail unless the page is changed after delete
        self.assertEquals(Assignment.objects.filter(id=self.testhelper.sub_period1_willbedeleted.id).count(), 0)

    def test_delete_notparentadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2)'],
                            assignments=['willbedeleted:admin(willbedeletedadm)'])
        self._loginToAssignment('willbedeletedadm', self.testhelper.sub_period1_willbedeleted.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.click_delete_button()
        self.waitForText('Only superusers can delete non-empty items') # Will time out and fail unless the dialog is shown

    def test_delete_not_empty(self):
        self.testhelper.add_to_path('uni;sub.period1.week1.g1:candidate(goodStud1):examiner(exam1).d1')
        self.testhelper.add_delivery('sub.period1.week1.g1', {'bad.py': ['print ', 'bah']})
        self._loginToAssignment('uniadmin', self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.click_delete_button()
        self.waitForText('Only superusers can delete non-empty items') # Will time out and fail unless the dialog is shown


class TestEditPublishingTime(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-3)'],
                            assignments=['week1:admin(week1admin)'])
        self.week1 = self.testhelper.sub_period1_week1
        self.loginTo('week1admin', '/assignment/{id}/'.format(id=self.week1.id))

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpublishingtime_widget .editablesidebarbox')
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpublishingtime_widget .editablesidebarbox .edit_link')
        button.click()

        panel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpublishingtimepanel')
        self.datefield = panel.find_element_by_css_selector('.devilry_extjsextras_datefield input')
        self.timefield = panel.find_element_by_css_selector('.devilry_extjsextras_timefield input')
        self.savebutton = panel.find_element_by_css_selector('.okbutton button')
        self.cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')

    def _set_datetime(self, date, time):
        self.datefield.clear()
        self.timefield.clear()
        self.datefield.send_keys(date)
        self.timefield.send_keys(time)

    def test_editpublishingtime(self):
        self.assertTrue('Publishing time' in self.selenium.page_source)
        self.assertTrue('Choose a time when time when students will be able to start adding deliveries on the assignment' in self.selenium.page_source)
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        isoday_yesterday = yesterday.date().isoformat()
        self._set_datetime(isoday_yesterday, '12:00')
        self.savebutton.click()
        self.waitForText('{isoday_yesterday} 12:00'.format(**vars())) # If this times out, it has not been updated
        week1 = Assignment.objects.get(pk=self.testhelper.sub_period1_week1.pk)
        self.assertEquals(week1.publishing_time.date(), yesterday.date())

    def test_editpublishingtime_notpublished(self):
        tomorrow = datetime.now() + timedelta(days=1)
        isoday_tomorrow = tomorrow.date().isoformat()
        self._set_datetime(isoday_tomorrow, '12:00')
        self.savebutton.click()
        self.waitForText('{isoday_tomorrow} 12:00'.format(**vars())) # If this times out, it has not been updated
        week1 = Assignment.objects.get(pk=self.testhelper.sub_period1_week1.pk)
        self.assertEquals(week1.publishing_time.date(), tomorrow.date())

    def test_cancel(self):
        self.cancelbutton.click()
        self.waitForDisplayed(self.readOnlyPanel)

    def test_editpublishingtime_errorhandling(self):
        self._set_datetime('2000-02-01', '12:00')
        self.savebutton.click()
        self.waitForText("The publishing time, 2000-02-01 12:00:00, is invalid")


class TestEditAnonymous(SubjectAdminSeleniumTestCase):

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-3)'],
                            assignments=['week1:admin(week1admin)'])
        self.week1 = self.testhelper.sub_period1_week1
        self.loginTo('week1admin', '/assignment/{id}/'.format(id=self.week1.id))

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymous_widget .editablesidebarbox')
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymous_widget .editablesidebarbox .edit_link')
        button.click()

        editanonymouspanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymouspanel')
        self.waitForDisplayed(editanonymouspanel)
        self.anonymouscheckbox = editanonymouspanel.find_element_by_css_selector('input.x-form-checkbox')
        self.savebutton = editanonymouspanel.find_element_by_css_selector('.okbutton button')
        self.cancelbutton = editanonymouspanel.find_element_by_css_selector('.cancelbutton button')

    def test_editanonymous(self):
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
        self.assertTrue('Not anonymous' in self.selenium.page_source)
        self.assertTrue('Examiners and students can see each other and communicate.' in self.selenium.page_source)
        self.anonymouscheckbox.click()
        self.savebutton.click()
        self.waitForText('>Anonymous') # If this times out, is has not been updated
        self.waitForText('Examiners and students can not see each other and they can not communicate.') # If this times out, is has not been updated
        self.assertTrue(Assignment.objects.get(pk=self.week1.pk).anonymous)

    def test_cancel(self):
        self.cancelbutton.click()
        self.waitForDisplayed(self.readOnlyPanel)

    def test_editanonymous_nochange(self):
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
        self.savebutton.click()
        self.waitForDisplayed(self.readOnlyPanel)
        self.waitForText('Not anonymous') # If this times out, it has not been updated
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
