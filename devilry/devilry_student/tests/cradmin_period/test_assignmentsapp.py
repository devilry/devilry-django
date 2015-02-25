from django.template import defaultfilters
from django.test import TestCase
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
from django_cradmin import crinstance

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder, \
    PeriodBuilder, AssignmentGroupBuilder


class TestAssignmentGroupListView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student_period', 'assignments', roleid=self.periodbuilder.period.id))

    def test_not_candidate_on_any_group(self):
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_is_candidate_on_group(self):
        self.periodbuilder.add_assignment('testassignment')\
            .add_group(students=[self.testuser])
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

    def test_render(self):
        groupbuilder = self.periodbuilder\
            .add_assignment(short_name='testassignment', long_name='Test Assignment')\
            .add_group(students=[self.testuser])
        deadline = groupbuilder.add_deadline_in_x_weeks(weeks=1).deadline
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1)').alltext_normalized,
            'Test Assignment')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) a')['href'],
            crinstance.reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='overview',
                roleid=groupbuilder.group.id))
        # self.assertEquals(
        #     selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
        #     defaultfilters.date(deadline.deadline, 'SHORT_DATETIME_FORMAT'))

    def test_no_deadlines(self):
        self.periodbuilder\
            .add_assignment(short_name='testassignment')\
            .add_group(students=[self.testuser])
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'No deadlines')
        self.assertTrue(
            selector.exists('#objecttableview-table tbody tr td:nth-child(2) .text-danger'))

    def test_waiting_for_deliveries_no_deliveries(self):
        self.periodbuilder\
            .add_assignment(short_name='testassignment')\
            .add_group(students=[self.testuser])\
            .add_deadline_in_x_weeks(weeks=1)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'Waiting for deliveries or for deadline to expire.')

    def test_waiting_for_feedback_no_deliveries(self):
        self.periodbuilder\
            .add_assignment(short_name='testassignment')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'Waiting for feedback.')

    def test_corrected_passed(self):
        self.periodbuilder\
            .add_assignment(short_name='testassignment')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(
                grade='Good',
                points=10,
                is_passing_grade=True,
                saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'Good (Passed)')

    def test_corrected_failed(self):
        self.periodbuilder\
            .add_assignment(short_name='testassignment')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(
                grade='Bad',
                points=1,
                is_passing_grade=False,
                saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'Bad (Failed)')
