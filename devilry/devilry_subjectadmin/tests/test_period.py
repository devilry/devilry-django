from datetime import datetime

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Period
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import RenameBasenodeTestMixin
from devilry.devilry_subjectadmin.tests.base import DeleteBasenodeTestMixin
from devilry.devilry_subjectadmin.tests.base import EditAdministratorsTestMixin


class PeriodTestCommonMixin(object):
    def browseToPeriod(self, id):
        self.browseTo('/period/{id}/'.format(id=id))

    def loginToPeriod(self, username, id):
        self.loginTo(username, '/period/{id}/'.format(id=id))


class TestPeriodOverview(SubjectAdminSeleniumTestCase, PeriodTestCommonMixin,
                         RenameBasenodeTestMixin, DeleteBasenodeTestMixin):
    renamebutton_id = 'periodRenameButton'
    deletebutton_id = 'periodDeleteButton'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck9000'],
                            periods=['period1:admin(period1admin):ln(Period One)'])

    def test_doesnotexists(self):
        self.login('uniadmin')
        self.browseToPeriod(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self.browseToPeriod(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_breadcrumb(self):
        self.login('period1admin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        breadcrumbtext = self.get_breadcrumbstring('duck9000')
        self.assertEquals(breadcrumbtext, ['All my subjects', 'duck9000.period1'])

    def _get_assignment_url(self, assignment):
        return '#/assignment/{0}/'.format(assignment.id)

    def test_list_of_assignments(self):
        self.testhelper.add_to_path('uni;duck9000.period1.a1:ln(Assignment One)')
        self.testhelper.add_to_path('uni;duck9000.period1.a2:ln(Assignment Two)')
        self.testhelper.add_to_path('uni;duck9000.period2.first:ln(First Assignment)')

        self.login('period1admin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForText('Period One')
        self.waitForCssSelector('li.devilry_assignment')

        assignmentlist = self.selenium.find_element_by_css_selector('.devilry_listofassignments')
        self.assertEquals(len(assignmentlist.find_elements_by_css_selector('li.devilry_assignment')), 2)
        self.assertTrue('Assignment One' in self.selenium.page_source)
        self.assertTrue('Assignment Two' in self.selenium.page_source)
        self.assertFalse('First Assignment' in self.selenium.page_source)
        self.assertIn(self._get_assignment_url(self.testhelper.duck9000_period1_a1), self.selenium.page_source)
        self.assertIn(self._get_assignment_url(self.testhelper.duck9000_period1_a2), self.selenium.page_source)
        self.assertNotIn(self._get_assignment_url(self.testhelper.duck9000_period2_first), self.selenium.page_source)

    def test_dangerous_panel(self):
        self.login('period1admin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.waitForText('Delete duck9000.period1')
        self.waitForText('Rename duck9000.period1')
        self.assertIn('Once you delete a ', self.selenium.page_source)
        self.assertIn('should not be done without a certain amount of consideration', self.selenium.page_source)

    def test_rename(self):
        self.login('period1admin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.rename_test_helper(self.testhelper.duck9000_period1)

    def test_rename_failure(self):
        self.login('period1admin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.rename_test_failure_helper()

    def test_delete(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['willbedeleted'])
        self.login('uniadmin')
        self.browseToPeriod(self.testhelper.sub_willbedeleted.id)
        delete_button = self.waitForAndFindElementByCssSelector('#periodDeleteButton')
        self.assertTrue(delete_button.is_displayed())
        periodurl = self.selenium.current_url
        self.perform_delete()
        self.waitFor(self.selenium, lambda s: s.current_url != periodurl) # Will time out and fail unless the page is changed after delete
        self.assertEquals(Period.objects.filter(id=self.testhelper.sub_willbedeleted.id).count(), 0)

    def test_delete_notparentadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['willbedeleted:admin(willbedeletedadm)'])
        self.login('willbedeletedadm')
        self.browseToPeriod(self.testhelper.sub_willbedeleted.id)
        delete_button = self.waitForAndFindElementByCssSelector('#periodDeleteButton')
        self.assertFalse(delete_button.is_displayed())

    def test_delete_not_empty(self):
        self.testhelper.add_to_path('uni;duck9000.period1.a1:ln(Assignment One)')
        self.login('uniadmin')
        self.browseToPeriod(self.testhelper.duck9000_period1.id)
        delete_button = self.waitForAndFindElementByCssSelector('#periodDeleteButton')
        self.assertFalse(delete_button.is_displayed())


class TestPeriodEditAdministrators(SubjectAdminSeleniumTestCase, PeriodTestCommonMixin,
                                   EditAdministratorsTestMixin):

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['sub'],
                            periods=['p1'])
        self.login('uniadmin')

    def getBasenode(self):
        return self.testhelper.sub_p1

    def browseToTestBasenode(self):
        self.browseToPeriod(self.getBasenode().id)


class TestPeriodEditDuration(SubjectAdminSeleniumTestCase, PeriodTestCommonMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'])
        self.p1 = self.testhelper.sub_p1
        self.p1.start_time = datetime(2005, 1, 1)
        self.p1.end_time = datetime(2006, 1, 1)
        self.p1.save()
        self.loginToPeriod('p1admin', self.p1.id)

        self.readOnlyPanel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editperiod_duration_widget .containerwithedittitle')

    def _click_edit(self):
        button = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editperiod_duration_widget .containerwithedittitle .edit_link')
        button.click()

        panel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editdurationpanel')
        self.start_time_datefield = panel.find_element_by_css_selector('.start_time_field .devilry_extjsextras_datefield input')
        self.start_time_timefield = panel.find_element_by_css_selector('.start_time_field .devilry_extjsextras_timefield input')
        self.end_time_datefield = panel.find_element_by_css_selector('.end_time_field .devilry_extjsextras_datefield input')
        self.end_time_timefield = panel.find_element_by_css_selector('.end_time_field .devilry_extjsextras_timefield input')
        self.savebutton = self.waitForAndFindElementByCssSelector('.okbutton button', within=panel)
        self.cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        self.editpanel = panel

    def _set_values(self, start_date, start_time, end_date, end_time):
        self.start_time_datefield.clear()
        self.start_time_timefield.clear()
        self.end_time_datefield.clear()
        self.end_time_timefield.clear()
        self.start_time_datefield.send_keys(start_date)
        self.start_time_timefield.send_keys(start_time)
        self.end_time_datefield.send_keys(end_date)
        self.end_time_timefield.send_keys(end_time)
        self.selenium.find_element_by_css_selector('body').click()

    def _get_durationdisplay(self):
        return self.readOnlyPanel.find_element_by_css_selector('.durationdisplay').text.strip()

    def test_render(self):
        self.waitForDisplayed(self.readOnlyPanel)
        duration = self._get_durationdisplay().split()
        self.assertEquals(duration[0], u'2005-01-01')
        self.assertEquals(duration[1], u'00:00')
        self.assertEquals(duration[3], u'2006-01-01')
        self.assertEquals(duration[4], u'00:00')

    def test_edit(self):
        self._click_edit()
        self._set_values(start_date='2000-12-24', start_time='12:00',
                         end_date='2001-11-22', end_time='16:00')
        self.savebutton.click()
        self.waitForDisplayed(self.readOnlyPanel)
        duration = self._get_durationdisplay().split()
        self.assertEquals(duration[0], u'2000-12-24')
        self.assertEquals(duration[1], u'12:00')
        self.assertEquals(duration[3], u'2001-11-22')
        self.assertEquals(duration[4], u'16:00')
        p1 = self.testhelper.reload_from_db(self.p1)
        self.assertEquals(p1.start_time, datetime(2000, 12, 24, 12, 0))
        self.assertEquals(p1.end_time, datetime(2001, 11, 22, 16, 0))

    def test_errorhandling(self):
        self._click_edit()
        self._set_values(start_date='', start_time='12:00',
                         end_date='2001-11-22', end_time='16:00')
        self.savebutton.click()
        self.waitFor(self.editpanel, lambda p: 'Start time: This field is required' in p.text)
