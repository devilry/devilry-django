from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Period

from .base import SubjectAdminSeleniumTestCase
from .base import RenameBasenodeTestMixin
from .base import DeleteBasenodeTestMixin



class TestPeriodOverview(SubjectAdminSeleniumTestCase, RenameBasenodeTestMixin, DeleteBasenodeTestMixin):
    renamebutton_id = 'periodRenameButton'
    deletebutton_id = 'periodDeleteButton'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['duck9000'],
                            periods=['period1:admin(period1admin):ln(Period One)'])

    def _browseToPeriod(self, id):
        self.browseTo('/period/{id}/'.format(id=id))

    def test_doesnotexists(self):
        self.login('uniadmin')
        self._browseToPeriod(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self._browseToPeriod(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_breadcrumb(self):
        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        breadcrumbtext = self.get_breadcrumbstring('duck9000')
        self.assertEquals(breadcrumbtext, ['All subjects', 'duck9000', 'period1'])

    def _get_assignment_url(self, assignment):
        return '#/assignment/{0}/'.format(assignment.id)

    def test_list_of_assignments(self):
        self.testhelper.add_to_path('uni;duck9000.period1.a1:ln(Assignment One)')
        self.testhelper.add_to_path('uni;duck9000.period1.a2:ln(Assignment Two)')
        self.testhelper.add_to_path('uni;duck9000.period2.first:ln(First Assignment)')

        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
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
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.waitForText('Delete duck9000.period1')
        self.waitForText('Rename duck9000.period1')
        self.assertIn('Once you delete a period, there is no going back', self.selenium.page_source)
        self.assertIn('Renaming a period should not done without a certain amount of consideration', self.selenium.page_source)

    def test_rename(self):
        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.rename_test_helper(self.testhelper.duck9000_period1)

    def test_rename_failure(self):
        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.rename_test_failure_helper()

    def test_delete(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['willbedeleted'])
        self.login('uniadmin')
        self._browseToPeriod(self.testhelper.sub_willbedeleted.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        periodurl = self.selenium.current_url
        self.perform_delete()
        self.waitFor(self.selenium, lambda s: s.current_url != periodurl) # Will time out and fail unless the page is changed after delete
        self.assertEquals(Period.objects.filter(id=self.testhelper.sub_willbedeleted.id).count(), 0)

    def test_delete_notparentadmin(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['willbedeleted:admin(willbedeletedadm)'])
        self.login('willbedeletedadm')
        self._browseToPeriod(self.testhelper.sub_willbedeleted.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.click_delete_button()
        self.waitForText('Only superusers can delete non-empty items') # Will time out and fail unless the dialog is shown

    def test_delete_not_empty(self):
        self.testhelper.add_to_path('uni;duck9000.period1.a1:ln(Assignment One)')
        self.login('uniadmin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')
        self.click_delete_button()
        self.waitForText('Only superusers can delete non-empty items') # Will time out and fail unless the dialog is shown
