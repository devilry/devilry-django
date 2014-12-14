from datetime import datetime, timedelta

from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models.deliverytypes import ELECTRONIC, NON_ELECTRONIC
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import RenameBasenodeTestMixin
from devilry.devilry_subjectadmin.tests.base import DeleteBasenodeTestMixin


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

    def test_no_students(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        overview = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.waitForText('This assignment has no students. You need to add students', within=overview)

    def test_shortcuts_render(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['period1'],
            assignments=['week2:pub(2):admin(week2admin)'],
            assignmentgroups=['g1:candidate(student1)']
        )
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.assertTrue('@@manage-students' in self.selenium.page_source)
        self.assertTrue('@@bulk-manage-deadlines' in self.selenium.page_source)
        self.assertTrue('@@passed-previous-period' in self.selenium.page_source)

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
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime_widget .text-warning')

    def test_published(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2)'],
                            assignments=['week2:admin(week2admin)'])
        self._loginToAssignment('week2admin', self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime_widget .text-success')


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

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpublishingtime_widget .markupmoreinfobox')
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpublishingtime_widget .edit_link')
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
        self.assertTrue('Choose a time when students will be able to start adding deliveries on the assignment' in self.selenium.page_source)
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

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymous_widget .containerwithedittitle')

    def _click_edit(self):
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymous_widget .containerwithedittitle .edit_link')
        button.click()

        editanonymouspanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editanonymouspanel')
        self.waitForDisplayed(editanonymouspanel)
        self.anonymouscheckbox = editanonymouspanel.find_element_by_css_selector('input.x-form-checkbox')
        self.savebutton = editanonymouspanel.find_element_by_css_selector('.okbutton button')
        self.cancelbutton = editanonymouspanel.find_element_by_css_selector('.cancelbutton button')

    def test_readonlypanel(self):
        self.waitFor(self.readOnlyPanel, lambda p: 'Not anonymous' in p.text)

    def test_editanonymous(self):
        self._click_edit()
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
        self.anonymouscheckbox.click()
        self.savebutton.click()
        self.waitFor(self.readOnlyPanel, lambda p: 'Anonymous' in p.text)
        self.assertTrue(Assignment.objects.get(pk=self.week1.pk).anonymous)

    def test_cancel(self):
        self._click_edit()
        self.cancelbutton.click()
        self.waitForDisplayed(self.readOnlyPanel)

    def test_editanonymous_nochange(self):
        self._click_edit()
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
        self.savebutton.click()
        self.waitForDisplayed(self.readOnlyPanel)
        self.waitForText('Not anonymous') # If this times out, it has been updated
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)





class TestEditDeadlineHandling(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-3)'],
                            assignments=['week1:admin(week1admin)'])
        self.week1 = self.testhelper.sub_period1_week1
        self.loginTo('week1admin', '/assignment/{id}/'.format(id=self.week1.id))

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editdeadline_handling_widget .containerwithedittitle')

    def _click_edit(self):
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editdeadline_handling_widget .containerwithedittitle .edit_link')
        button.click()

        editdeadline_handlingpanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editdeadline_handlingpanel')
        self.waitForDisplayed(editdeadline_handlingpanel)
        self.deadline_handlingcheckbox = editdeadline_handlingpanel.find_element_by_css_selector('input.x-form-checkbox')
        self.savebutton = editdeadline_handlingpanel.find_element_by_css_selector('.okbutton button')
        self.cancelbutton = editdeadline_handlingpanel.find_element_by_css_selector('.cancelbutton button')

    def test_readonlypanel(self):
        self.assertEquals(Assignment.objects.get(pk=self.week1.pk).deadline_handling, ELECTRONIC)
        self.waitFor(self.readOnlyPanel, lambda p: 'Soft deadlines' in p.text)

    def test_editdeadline_handling(self):
        self._click_edit()
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).deadline_handling)
        self.deadline_handlingcheckbox.click()
        self.savebutton.click()
        self.waitFor(self.readOnlyPanel, lambda p: 'Hard deadlines' in p.text)
        self.assertEquals(Assignment.objects.get(pk=self.week1.pk).deadline_handling, NON_ELECTRONIC)

    def test_cancel(self):
        self._click_edit()
        self.cancelbutton.click()
        self.waitForDisplayed(self.readOnlyPanel)

    def test_editdeadline_handling_nochange(self):
        self._click_edit()
        self.assertEquals(Assignment.objects.get(pk=self.week1.pk).deadline_handling, ELECTRONIC)
        self.savebutton.click()
        self.waitForDisplayed(self.readOnlyPanel)
        self.waitForText('Soft deadlines') # If this times out, it has been updated
        self.assertEquals(Assignment.objects.get(pk=self.week1.pk).deadline_handling, ELECTRONIC)
