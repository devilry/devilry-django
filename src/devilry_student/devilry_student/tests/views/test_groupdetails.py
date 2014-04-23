from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
from devilry_developer.testhelpers.soupselect import normalize_whitespace
# from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.login import LoginTestCaseMixin
from devilry_developer.testhelpers.datebuilder import DJANGO_ISODATETIMEFORMAT
from devilry_developer.testhelpers.datebuilder import isoformat_datetime
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder



class TestGroupDetailsView(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _geturl(self, id):
        return reverse('devilry_student_groupdetails', args=[id])

    def test_not_authenticated(self):
        response = self.client.get(self._geturl(1))
        self.assertEquals(response.status_code, 302)

    def test_authenticated_and_candidate(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser]).group
        response = self.get_as(self.testuser, self._geturl(group.id))
        self.assertEquals(response.status_code, 200)

    def test_authenticated_not_candidate(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group().group
        response = self.get_as(self.testuser, self._geturl(group.id))
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1', long_name='Week One')\
            .add_group(students=[self.testuser]).group
        html = self.get_as(self.testuser, self._geturl(group.id)).content
        self.assertEquals(cssGet(html, 'h1').text.strip(), 'Week One')

    def test_breadcrumb(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser]).group
        html = self.get_as(self.testuser, self._geturl(group.id)).content
        self.assertEquals(
            [a.text.strip() for a in cssFind(html, '.breadcrumb li a')],
            ['Student', 'Browse', 'duck1010 - active'])

    def test_deadline_and_delivery_order(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testuser])
        
        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=4)
        delivery1 = deadline1builder.add_delivery_x_hours_before_deadline(hours=10).delivery
        delivery2 = deadline1builder.add_delivery_x_hours_before_deadline(hours=8).delivery
        
        deadline2builder = groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        delivery3 = deadline2builder.add_delivery_x_hours_before_deadline(hours=5).delivery
        delivery4 = deadline2builder.add_delivery_x_hours_before_deadline(hours=3).delivery

        with self.settings(DATETIME_FORMAT=DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            html = self.get_as(self.testuser, self._geturl(groupbuilder.group.id)).content

        self.assertEquals(
            [normalize_whitespace(e.text) for e in cssFind(html, '#devilry_student_groupdetails_deadlines h2')],
            [
                'Deadline 2: {}'.format(isoformat_datetime(deadline2builder.deadline.deadline)),
                'Deadline 1: {}'.format(isoformat_datetime(deadline1builder.deadline.deadline)),
            ]
        )
        self.assertEquals(
            [e['data-id'] for e in cssFind(html, '#devilry_student_groupdetails_deadlines a')],
            [str(delivery4.id), str(delivery3.id), str(delivery2.id), str(delivery1.id)]
        )
        self.assertEquals(
            [normalize_whitespace(e.text) for e in cssFind(html, '#devilry_student_groupdetails_deadlines a')],
            ['Delivery #4', 'Delivery #3', 'Delivery #2', 'Delivery #1']
        )

    def test_delivery_rendering_no_feedback(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_x_weeks_ago(weeks=1).add_delivery()
        html = self.get_as(self.testuser, self._geturl(groupbuilder.group.id)).content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '#devilry_student_groupdetails_deadlines a').text),
            'Delivery #1')
        self.assertEquals(
            normalize_whitespace(cssGet(html, '#devilry_student_groupdetails_deadlines .last-feedback').text),
            'No feedback')

    def test_delivery_rendering_passed_feedback(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery()\
            .add_passed_feedback(saved_by=UserBuilder('testexaminer').user)
        html = self.get_as(self.testuser, self._geturl(groupbuilder.group.id)).content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '#devilry_student_groupdetails_deadlines .last-feedback').text),
            'Passed')

    def test_delivery_rendering_failed_feedback(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery()\
            .add_failed_feedback(saved_by=UserBuilder('testexaminer').user)
        html = self.get_as(self.testuser, self._geturl(groupbuilder.group.id)).content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '#devilry_student_groupdetails_deadlines .last-feedback').text),
            'Failed')

    def test_delivery_rendering_points_feedback(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', grading_system_plugin_id='testing')\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery()\
            .add_feedback(
                saved_by=UserBuilder('testexaminer').user,
                points=10,
                grade='A',
                is_passing_grade=True)
        html = self.get_as(self.testuser, self._geturl(groupbuilder.group.id)).content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '#devilry_student_groupdetails_deadlines .last-feedback').text),
            'Passed(A)')