from django.contrib.humanize.templatetags.humanize import naturaltime
from django.test import TestCase
from django.utils.formats import date_format
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
from django_cradmin import crinstance

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder, \
    AssignmentGroupBuilder


class TestRecentFeedbacks(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student', 'recentfeedbacks', roleid=self.testuser.id))

    def test_only_owned(self):
        AssignmentGroupBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group(studentuser=UserBuilder('otheruser').user)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_passed_A_feedback(saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_only_with_feedback(self):
        AssignmentGroupBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group(studentuser=self.testuser)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_render(self):
        deadlinebuilder = NodeBuilder.quickadd_ducku()\
            .add_subject(short_name='atestcourse', long_name='A Test Course')\
            .add_6month_active_period(short_name='testperiod', long_name='Test Period')\
            .add_assignment('testassignment', long_name='Test Assignment One')\
            .add_group(students=[self.testuser])\
            .add_deadline_in_x_weeks(weeks=1)
        deliverybuilder = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1)
        feedback = deliverybuilder.add_passed_A_feedback(saved_by=UserBuilder('testexaminer').user).feedback
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) a').alltext_normalized,
            'Test Assignment One - Delivery#1')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) a')['href'],
            crinstance.reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='deliveries',
                roleid=deliverybuilder.delivery.deadline.assignment_group_id,
                viewname='deliverydetails',
                kwargs={'pk': deliverybuilder.delivery.pk}))
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'A Test Course - Test Period')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(3)').alltext_normalized,
            'atestcourse - testperiod')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(4)').alltext_normalized,
            htmls.normalize_whitespace(naturaltime(feedback.save_timestamp)
                                       + date_format(feedback.save_timestamp, "SHORT_DATETIME_FORMAT")))

    def test_render_feedback_passed(self):
        AssignmentGroupBuilder.quickadd_ducku_duck1010_active_assignment1_group(self.testuser)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(
                points=10,
                grade='Good',
                is_passing_grade=True,
                saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)

        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) '
                         '.devilry-student-delivery-summarycolumn-feedback').alltext_normalized,
            'Good (passed)')
        self.assertTrue(
            selector.exists('#objecttableview-table tbody tr td:nth-child(1) .text-success'))

    def test_render_feedback_failed(self):
        AssignmentGroupBuilder.quickadd_ducku_duck1010_active_assignment1_group(self.testuser)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_feedback(
                points=1,
                grade='Bad',
                is_passing_grade=False,
                saved_by=UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)

        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)
        # selector.one('#objecttableview-table tbody tr td:nth-child(1)').prettyprint()
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) '
                         '.devilry-student-delivery-summarycolumn-feedback').alltext_normalized,
            'Bad (failed)')
        self.assertTrue(
            selector.exists('#objecttableview-table tbody tr td:nth-child(1) .text-warning'))
