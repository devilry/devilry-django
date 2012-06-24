from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



class TestPeriodOverview(SubjectAdminSeleniumTestCase):
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
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('403: FORBIDDEN' in self.selenium.page_source)

    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self.login('grandma')
        self._browseToPeriod(100000)
        self.waitForCssSelector('.alertmessagelist')
        self.assertTrue('404: NOT FOUND' in self.selenium.page_source)

    def test_breadcrumb(self):
        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.breadcrumb')
        def breadcrumbLoaded(breadcrumb):
            return 'duck9000' in breadcrumb.text
        breadcrumb = self.selenium.find_element_by_css_selector('.breadcrumb')
        self.waitFor(breadcrumb, breadcrumbLoaded)
        self.assertEquals(breadcrumb.text, 'You are here:Subjectadmin/All subjects/duck9000/period1')

    def test_menubar(self):
        self.login('period1admin')
        self._browseToPeriod(self.testhelper.duck9000_period1.id)
        self.waitForCssSelector('.devilry_periodoverview')
        advancedButton = self.selenium.find_element_by_css_selector('#menubarAdvancedButton button')
        advancedButton.click()
        self.waitForText('Delete duck9000.period1')
        self.waitForText('Rename duck9000.period1')
        self.assertEquals(self.selenium.find_element_by_css_selector('#menubarAdvancedDeleteButton .x-menu-item-text').text,
                          'Delete duck9000.period1')
        self.assertEquals(self.selenium.find_element_by_css_selector('#menubarAdvancedRenameButton .x-menu-item-text').text,
                          'Rename duck9000.period1')

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
