import unittest

from django.conf import settings

from devilry.apps.core.models import Assignment
from devilry.apps.core.testhelper import TestHelper
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

    @unittest.skipIf(
        settings.SELENIUM_BROWSER == 'phantomjs',
        'This does not work with phantomjs for some reason')
    def test_doesnotexists_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self._loginToAssignment('grandma', 1000)
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
        self.testhelper.add(
            nodes='uni',
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
        deletebutton = self.waitForAndFindElementByCssSelector(self.get_delete_button_css_selector())
        self.assertFalse(deletebutton.is_displayed())

    def test_delete_not_empty(self):
        self.testhelper.add_to_path('uni;sub.period1.week1.g1:candidate(goodStud1):examiner(exam1).d1')
        self.testhelper.add_delivery('sub.period1.week1.g1', {'bad.py': ['print ', 'bah']})
        self._loginToAssignment('uniadmin', self.testhelper.sub_period1_week1.id)
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        deletebutton = self.waitForAndFindElementByCssSelector(self.get_delete_button_css_selector())
        self.assertFalse(deletebutton.is_displayed())
