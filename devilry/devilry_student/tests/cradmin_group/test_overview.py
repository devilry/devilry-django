from django.test import TestCase, RequestFactory
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
from devilry.apps.core.models import Assignment
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestOverview(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student_group', 'overview', roleid=self.groupbuilder.group.id))

    def test_status_waiting_for_deliveries(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.assertEquals(self.groupbuilder.group.get_status(), 'waiting-for-deliveries')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-waiting-for-deliveries'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-waiting-for-deliveries').alltext_normalized,
            'This assignment is open for deliveries. Add delivery.')
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-waiting-for-deliveries a')['href'],
            reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='deliveries',
                roleid=self.groupbuilder.group.id,
                viewname='add-delivery'))

    def test_status_waiting_for_feedback_hard_deadlines(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.assertEquals(self.groupbuilder.group.get_status(), 'waiting-for-feedback')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-waiting-for-feedback'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-waiting-for-feedback').alltext_normalized,
            'Your assignment is waiting for feedback.')

    def test_status_waiting_for_feedback_soft_deadlines(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_SOFT)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.assertEquals(self.groupbuilder.group.get_status(), 'waiting-for-feedback')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-waiting-for-feedback'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-waiting-for-feedback').alltext_normalized,
            'Your assignment is waiting for feedback. The active deadline has expired, '
            'but this assignment is configured with soft deadines so you can still add deliveries. Add delivery.')
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-waiting-for-feedback a')['href'],
            reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='deliveries',
                roleid=self.groupbuilder.group.id,
                viewname='add-delivery'))

    def test_status_corrected_passed(self):
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_feedback(saved_by=UserBuilder('testexaminer').user,
                                     grade='10/20',
                                     is_passing_grade=True,
                                     points=20)
        self.groupbuilder.add_students(self.testuser)
        self.assertEquals(self.groupbuilder.group.get_status(), 'corrected')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-corrected'))
        self.assertTrue(selector.exists('.devilry-student-groupoverview-corrected-passed'))
        self.assertTrue(selector.exists
                        ('.django-cradmin-container-fluid-focus.django-cradmin-container-fluid-focus-success'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-corrected').alltext_normalized,
            'This assignment is corrected, and the final grade is: 10/20 (passed)')
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-corrected a')['href'],
            reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='deliveries',
                roleid=self.groupbuilder.group.id,
                viewname='deliverydetails',
                kwargs={'pk': deliverybuilder.delivery.id}))

    def test_status_corrected_failed(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(saved_by=UserBuilder('testexaminer').user,
                          grade='2/20',
                          is_passing_grade=False,
                          points=2)
        self.groupbuilder.add_students(self.testuser)
        self.assertEquals(self.groupbuilder.group.get_status(), 'corrected')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-corrected'))
        self.assertTrue(selector.exists('.devilry-student-groupoverview-corrected-failed'))
        self.assertTrue(selector.exists
                        ('.django-cradmin-container-fluid-focus.django-cradmin-container-fluid-focus-warning'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-corrected').alltext_normalized,
            'This assignment is corrected, and the final grade is: 2/20 (failed)')

    def test_status_closed_without_feedback(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.groupbuilder.update(is_open=False)
        self.assertEquals(self.groupbuilder.group.get_status(), 'closed-without-feedback')
        response = self._get_as('testuser')
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-groupoverview-closed-without-feedback'))
        self.assertEquals(
            selector.one('.devilry-student-groupoverview-closed-without-feedback').alltext_normalized,
            'Your assignment has been closed without feedback.')
