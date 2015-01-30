from django.test import TestCase, RequestFactory
import htmls
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestOverview(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def test_render_hard_deadline_not_expired(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_delivery_list_hard_deadline_expired_message'))

    def test_render_hard_deadline_expired(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_delivery_list_hard_deadline_expired_message'))
