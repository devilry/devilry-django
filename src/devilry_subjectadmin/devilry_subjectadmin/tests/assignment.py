from datetime import datetime, timedelta
from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase
from .base import RenameBasenodeTestMixin
from .base import DeleteBasenodeTestMixin



class TestAssignment(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _browseToAssignment(self, id):
        self.browseTo('/assignment/{id}/'.format(id=id))

    def test_doesnotexists(self):
        self.testhelper.create_user('normal')
        self.login('normal')
        self._browseToAssignment(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self._browseToAssignment(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_shortcuts_render(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self.login('week2admin')
        self._browseToAssignment(self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.assertTrue('Manage students' in self.selenium.page_source)
        self.assertTrue('Manage deadlines' in self.selenium.page_source)

    def test_title(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self.login('week2admin')
        self._browseToAssignment(self.testhelper.sub_period1_week2.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.assertEquals(self.selenium.title, 'sub.period1.week2 - Devilry')

    def test_notpublished(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1'],
                            assignments=['week2:pub(2):admin(week2admin)'])
        self.login('week2admin')
        self._browseToAssignment(self.testhelper.sub_period1_week2.id)
        self.waitForText('>Not published')

    def test_published(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2)'],
                            assignments=['week2:admin(week2admin)'])
        self.login('week2admin')
        self._browseToAssignment(self.testhelper.sub_period1_week2.id)
        self.waitForText('>Published')


class TestAssignmentDangerous(SubjectAdminSeleniumTestCase, RenameBasenodeTestMixin, DeleteBasenodeTestMixin):
    renamebutton_id = 'assignmentRenameButton'
    deletebutton_id = 'assignmentDeleteButton'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['sub'],
                            periods=['period1:begins(-2):admin(p1admin)'],
                            assignments=['week1:admin(weekadmin)'])

    def _browseToAssignment(self, id):
        self.browseTo('/assignment/{id}/'.format(id=id))

    def test_rename(self):
        self.login('weekadmin')
        self._browseToAssignment(self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.rename_test_helper(self.testhelper.sub_period1_week1)

    def test_rename_failure(self):
        self.login('weekadmin')
        self._browseToAssignment(self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.rename_test_failure_helper()

    def test_delete(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['period1:begins(-2):admin(p1admin)'],
                            assignments=['willbedeleted'])
        self.login('p1admin')
        self._browseToAssignment(self.testhelper.sub_period1_willbedeleted.id)
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
        self.login('willbedeletedadm')
        self._browseToAssignment(self.testhelper.sub_period1_willbedeleted.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        self.click_delete_button()
        self.waitForText('Only superusers can delete non-empty items') # Will time out and fail unless the dialog is shown

    def test_delete_not_empty(self):
        self.testhelper.add_to_path('uni;sub.period1.week1.g1:candidate(goodStud1):examiner(exam1).d1')
        self.testhelper.add_delivery('sub.period1.week1.g1', {'bad.py': ['print ', 'bah']})
        self.login('uniadmin')
        self._browseToAssignment(self.testhelper.sub_period1_week1.id)
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
        self.login('week1admin')

        self.browseTo('/assignment/1/')
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime_widget button')
        button = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_editpublishingtime_widget button')
        button.click()
        self.waitForCssSelector('.devilry_subjectadmin_editpublishingtime')

        editpublishingtime_window = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_editpublishingtime')
        self.datefield = editpublishingtime_window.find_element_by_css_selector('.devilry_extjsextras_datefield input')
        self.timefield = editpublishingtime_window.find_element_by_css_selector('.devilry_extjsextras_timefield input')
        self.savebutton = editpublishingtime_window.find_element_by_css_selector('.devilry_extjsextras_savebutton button')
        self.cancelbutton = editpublishingtime_window.find_element_by_css_selector('.devilry_extjsextras_cancelbutton')
        self.editpublishingtime_window = editpublishingtime_window

    def _set_datetime(self, date, time):
        self.datefield.clear()
        self.timefield.clear()
        self.datefield.send_keys(date)
        self.timefield.send_keys(time)

    def test_editpublishingtime(self):
        self.assertTrue('Published' in self.selenium.page_source)
        self.assertTrue('Choose a time when time when students will be able to start adding deliveries on the assignment' in self.selenium.page_source)
        yesterday = datetime.now() - timedelta(days=1)
        isoday_yesterday = yesterday.date().isoformat()
        self._set_datetime(isoday_yesterday, '12:00')
        self.savebutton.click()
        self.waitForText('Publishing time was {isoday_yesterday} 12:00'.format(**vars())) # If this times out, it has not been updated
        week1 = Assignment.objects.get(pk=self.testhelper.sub_period1_week1.pk)
        self.assertEquals(week1.publishing_time.date(), yesterday.date())

    def test_editpublishingtime_notpublished(self):
        tomorrow = datetime.now() + timedelta(days=1)
        isoday_tomorrow = tomorrow.date().isoformat()
        self._set_datetime(isoday_tomorrow, '12:00')
        self.savebutton.click()
        self.waitForText('Will be published {isoday_tomorrow} 12:00'.format(**vars())) # If this times out, it has not been updated
        week1 = Assignment.objects.get(pk=self.testhelper.sub_period1_week1.pk)
        self.assertEquals(week1.publishing_time.date(), tomorrow.date())

    def test_cancel(self):
        self.failIfCssSelectorFound(self.editpublishingtime_window, '.x-tool-close')  # Make sure window does not have closable set to true
        self.cancelbutton.click()
        self.assertFalse('.devilry_subjectadmin_editpublishingtime' in self.selenium.page_source)

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
        self.login('week1admin')

        self.week1 = self.testhelper.sub_period1_week1

        self.browseTo('/assignment/{0}/'.format(self.testhelper.sub_period1_week1.id))
        self.waitForCssSelector('.devilry_subjectadmin_editanonymous_widget .edit_link')
        button = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_editanonymous_widget .edit_link')
        button.click()
        self.waitForCssSelector('.devilry_subjectadmin_editanonymous')

        editanonymous_window = self.selenium.find_element_by_css_selector('.devilry_subjectadmin_editanonymous')
        self.anonymouscheckbox = editanonymous_window.find_element_by_css_selector('input.x-form-checkbox')
        self.savebutton = editanonymous_window.find_element_by_css_selector('.devilry_extjsextras_savebutton button')
        self.cancelbutton = editanonymous_window.find_element_by_css_selector('.devilry_extjsextras_cancelbutton')
        self.editanonymous_window = editanonymous_window

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
        self.failIfCssSelectorFound(self.editanonymous_window, '.x-tool-close') # Make sure window does not have closable set to true
        self.cancelbutton.click()
        self.assertFalse('.devilry_subjectadmin_editanonymous' in self.selenium.page_source)

    def test_editanonymous_nochange(self):
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
        self.savebutton.click()
        self.waitForText('Not anonymous') # If this times out, it has not been updated
        self.assertFalse(Assignment.objects.get(pk=self.week1.pk).anonymous)
