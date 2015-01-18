from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_student.cradmin_group import deliveriesapp

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestDeliveryListView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def _mock_get_request(self):
        request = self.factory.get('/test')
        request.user = self.testuser
        request.cradmin_role = self.groupbuilder.group
        request.cradmin_app = mock.MagicMock()
        request.session = mock.MagicMock()
        response = deliveriesapp.DeliveryListView.as_view()(request)
        return response

    def test_list_no_deliveries(self):
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#objecttableview-table'))
        self.assertFalse(selector.exists('#objecttableview-table tbody tr'))

    def test_list_has_deliveries(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 2)
        self.assertEquals(selector.count('.devilry-student-deliveriesapp-summarycolumn'), 2)

    def test_render_no_feedback(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('.devilry-student-deliveriesapp-summarycolumn-feedback'))
        self.assertTrue(selector.exists('.devilry-student-deliveriesapp-summarycolumn-no-feedback'))
        self.assertEquals(
            selector.one('.devilry-student-deliveriesapp-summarycolumn-no-feedback').alltext_normalized,
            'No feedback')

    def test_render_has_feedback(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        delivery = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        delivery.add_feedback(
            points=10,
            grade='Good',
            is_passing_grade=True,
            saved_by=self.testuser)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('.devilry-student-deliveriesapp-summarycolumn-no-feedback'))

        self.assertTrue(selector.exists('.devilry-student-deliveriesapp-summarycolumn-feedback'))
        self.assertTrue(selector.exists('.devilry-student-deliveriesapp-summarycolumn-feedback-grade'))
        self.assertTrue(selector.exists('.devilry-student-deliveriesapp-summarycolumn-feedback-is_passing_grade'))
        self.assertEquals(
            selector.one('.devilry-student-deliveriesapp-summarycolumn-feedback-grade').alltext_normalized,
            'Good')
        self.assertEquals(
            selector.one('.devilry-student-deliveriesapp-summarycolumn-feedback-is_passing_grade').alltext_normalized,
            'passed')

    def test_render_deadline_expired_hard_deadlines(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_delivery_list_hard_deadline_expired_message'))
