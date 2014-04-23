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


    # def test_waiting_for_deliveries_rendering(self):
    #     deadline = SubjectBuilder.quickadd_ducku_duck1010(
    #             long_name='DUCK 1010')\
    #         .add_6month_active_period(
    #             long_name='Springtest')\
    #         .add_assignment('week1')\
    #         .add_group(students=[self.testuser.user])\
    #         .add_deadline_in_x_weeks(weeks=1).deadline
    #     with self.settings(DATETIME_FORMAT=DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
    #         html = self.get_as(self.testuser.user, self.url).content
    #     self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 1)
    #     self.assertEquals(
    #         cssGet(html, '#devilry_student_active_assignmentlist li a').text.strip(),
    #         'duck1010 - week1')
    #     self.assertEquals(
    #         cssGet(html, '#devilry_student_active_assignmentlist li .subject_and_period').text.strip(),
    #         'DUCK 1010 - Springtest')
    #     self.assertIn(
    #         isoformat_datetime(deadline.deadline),
    #         cssGet(html, '#devilry_student_active_assignmentlist li .deadline').text.strip())

    # def test_waiting_for_deliveries_only_where_student(self):
    #     assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_assignment('week1')
    #     assignmentbuilder.add_group(students=[self.testuser.user])\
    #         .add_deadline_in_x_weeks(weeks=1)
    #     assignmentbuilder.add_group(students=[UserBuilder('otheruser').user])\
    #         .add_deadline_in_x_weeks(weeks=1)
    #     html = self.get_as(self.testuser.user, self.url).content
    #     self.assertEquals(len(cssFind(html, '#devilry_student_active_assignmentlist li')), 1)


