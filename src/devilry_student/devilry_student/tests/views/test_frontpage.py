from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
# from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.login import LoginTestCaseMixin
from devilry_developer.testhelpers.datebuilder import DJANGO_ISODATETIMEFORMAT
from devilry_developer.testhelpers.datebuilder import isoformat_datetime
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder



class TestFrontpage(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.url = reverse('devilry_student')
        self.testuser = UserBuilder('testuser')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_authenticated(self):
        response = self.get_as(self.testuser.user, self.url)
        self.assertEquals(response.status_code, 200)

    def test_waiting_for_deliveries_rendering(self):
        deadline = SubjectBuilder.quickadd_ducku_duck1010(
                long_name='DUCK 1010')\
            .add_6month_active_period(
                long_name='Springtest')\
            .add_assignment('week1')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=1).deadline
        with self.settings(DATETIME_FORMAT=DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 1)
        self.assertEquals(
            cssGet(html, '#devilry_student_active_assignmentlist li a').text.strip(),
            'duck1010 - week1')
        self.assertEquals(
            cssGet(html, '#devilry_student_active_assignmentlist li .subject_and_period').text.strip(),
            'DUCK 1010 - Springtest')
        self.assertIn(
            isoformat_datetime(deadline.deadline),
            cssGet(html, '#devilry_student_active_assignmentlist li .deadline').text.strip())

    def test_waiting_for_deliveries_only_active_periods(self):
        SubjectBuilder.quickadd_ducku_duck1010()\
            .add_6month_lastyear_period()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=1)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 0)

    def test_waiting_for_deliveries_only_where_student(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')
        assignmentbuilder.add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=1)
        assignmentbuilder.add_group(students=[UserBuilder('otheruser').user])\
            .add_deadline_in_x_weeks(weeks=1)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 1)

    def test_only_where_waiting_for_deliveries(self):
        SubjectBuilder.quickadd_ducku_duck1010()\
            .add_6month_lastyear_period()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_x_weeks_ago(weeks=1) # Deadline in past - waiting for feedback, not deliveries
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 0)

    def test_active_assignments_order_by_closest_deadline(self):
        periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        periodbuilder.add_assignment('week3')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=3)
        periodbuilder.add_assignment('week1')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=1)
        periodbuilder.add_assignment('week2')\
            .add_group(students=[self.testuser.user])\
            .add_deadline_in_x_weeks(weeks=2)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(
            [e.text.strip() for e in cssFind(html, '#devilry_student_active_assignmentlist li a')],
            ['duck1010 - week1', 'duck1010 - week2', 'duck1010 - week3'])

    def test_none_waiting_for_deliveries_message(self):        
        html = self.get_as(self.testuser.user, self.url).content
        self.assertTrue(
            cssExists(html, '#devilry_student_frontpage_none_waiting_for_deliveries_message'))


    def test_browse_no_active_periods(self):
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(
            len(cssFind(html, '#devilry_student_frontpage_browselist li')), 1)

    def test_browse_active_period_rendering(self):
        SubjectBuilder.quickadd_ducku_duck1010(
                long_name='DUCK 1010')\
            .add_6month_active_period(
                long_name='Springtest')\
            .add_relatedstudents(self.testuser.user)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(
            len(cssFind(html, '#devilry_student_frontpage_browselist li')), 2)
        self.assertEquals(
            cssFind(html, '#devilry_student_frontpage_browselist li a')[0].text.strip(),
            'DUCK 1010 - Springtest')

    def test_browse_only_active_periods(self):
        subjectbuilder = SubjectBuilder.quickadd_ducku_duck1010()
        subjectbuilder.add_6month_active_period()\
            .add_relatedstudents(self.testuser.user)
        subjectbuilder.add_6month_lastyear_period()\
            .add_relatedstudents(self.testuser.user)
        subjectbuilder.add_6month_nextyear_period()\
            .add_relatedstudents(self.testuser.user)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(
            len(cssFind(html, '#devilry_student_frontpage_browselist li')), 2)
        self.assertEquals(
            cssFind(html, '#devilry_student_frontpage_browselist li a')[0].text.strip(),
            'duck1010 - active')

    def test_browse_active_ordering(self):
        first_start = DateTimeBuilder.now().minus(days=30*3)
        second_start = DateTimeBuilder.now().minus(days=30*2)
        end_time = DateTimeBuilder.now().plus(days=10)
        nodebuilder = NodeBuilder('ducku')

        nodebuilder.add_subject('duckb', long_name='DUCK B')\
            .add_period(
                short_name='x', long_name='x',
                start_time=second_start, end_time=end_time)\
            .add_relatedstudents(self.testuser.user)
        nodebuilder.add_subject('duckc', long_name='DUCK C')\
            .add_period(
                short_name='x', long_name='x',
                start_time=first_start, end_time=end_time)\
            .add_relatedstudents(self.testuser.user)
        nodebuilder.add_subject('ducka', long_name='DUCK A')\
            .add_period(
                short_name='x', long_name='x',
                start_time=second_start, end_time=end_time)\
            .add_relatedstudents(self.testuser.user)

        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(
            [a.text.strip() for a in cssFind(html, '#devilry_student_frontpage_browselist li a')],
            ['DUCK A - x', 'DUCK B - x', 'DUCK C - x', 'Browse all'])

    # def test_browse_active_period_latest_feedback(self):
    #     SubjectBuilder.quickadd_ducku_duck1010()\
    #         .add_6month_active_period()\
    #         .add_assignment('week1')\
    #         .add_group(students=[self.testuser.user])\
    #         .add_deadline_x_weeks_ago(weeks=1)\
    #         .add_delivery()\
    #         .add_passed_feedback(saved_by=UserBuilder('testexaminer').user)
    #     html = self.get_as(self.testuser.user, self.url).content
    #     self.assertEquals(
    #         cssFind(html, '#devilry_student_frontpage_browselist li .last-feedback')[0].text.strip(),
    #         'Latest feedback: week1 ')
