from django.test import TestCase
from django.utils.formats import date_format
from django_cradmin.crinstance import reverse_cradmin_url
import htmls

from devilry.apps.core.models import Assignment
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder, NodeBuilder


class TestWaitingForDeliveries(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student', 'waitingfordeliveries', roleid=self.testuser.id))

    def test_waiting_for_deliveries_only_owned(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')\
            .add_group(students=[UserBuilder('otheruser').user])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_waiting_for_deliveries_render(self):
        deadlinebuilder = NodeBuilder.quickadd_ducku()\
            .add_subject(short_name='atestcourse', long_name='A Test Course')\
            .add_6month_active_period(short_name='testperiod', long_name='Test Period')\
            .add_assignment('testassignment', long_name='Test Assignment One')\
            .add_group(students=[self.testuser])\
            .add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        # selector.one('#objecttableview-table tbody tr td:nth-child(1)').prettyprint()
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1)').alltext_normalized,
            'Test Assignment One')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'A Test Course - Test Period')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(3)').alltext_normalized,
            'atestcourse - testperiod')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(4) .text-success').alltext_normalized,
            u'6 days, 23 hours from now')
        self.assertTrue(selector.exists('#objecttableview-table tbody tr td:nth-child(4) .text-success'))

    def test_corrected_not_included(self):
        deliverybuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')\
            .add_group(students=[self.testuser])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)

        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        deliverybuilder.add_passed_A_feedback(saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_hard_deadlines_expired_not_included(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment',
                            deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        assignmentbuilder.add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)

        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_soft_deadlines_expired_included(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment',
                            deadline_handling=Assignment.DEADLINEHANDLING_SOFT)
        assignmentbuilder.add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)

        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

    def test_soft_deadlines_expired_only_owned(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment',
                            deadline_handling=Assignment.DEADLINEHANDLING_SOFT)
        assignmentbuilder.add_group(students=[UserBuilder('otheruser').user])\
            .add_deadline_x_weeks_ago(weeks=1)

        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_soft_deadlines_expired_render(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment',
                            deadline_handling=Assignment.DEADLINEHANDLING_SOFT)
        assignmentbuilder.add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1)

        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertTrue(
            selector.exists('#objecttableview-table tbody tr td:nth-child(4) .text-warning'))
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(4) .text-warning').alltext_normalized,
            u'1 week ago')
