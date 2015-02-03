from django.test import TestCase
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
from django_cradmin import crinstance

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder, \
    PeriodBuilder, SubjectBuilder, AssignmentGroupBuilder


class TestAllPeriods(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student', 'allperiods', roleid=self.testuser.id))

    def test_not_student_on_anything(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 0)

    def test_is_relatedstudent(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

    def test_is_not_relatedstudent_but_registered_on_group(self):
        AssignmentGroupBuilder.quickadd_ducku_duck1010_active_assignment1_group(studentuser=self.testuser)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

    def test_render(self):
        periodbuilder = NodeBuilder.quickadd_ducku()\
            .add_subject(short_name='atestcourse', long_name='A Test Course')\
            .add_6month_active_period(short_name='testperiod', long_name='Test Period')\
            .add_relatedstudents(self.testuser)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1)').alltext_normalized,
            'A Test Course - Test Period')
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(1) a')['href'],
            crinstance.reverse_cradmin_url(
                instanceid='devilry_student_period',
                appname='assignments',
                roleid=periodbuilder.period.id))

    def test_is_active(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'Yes')

    def test_is_not_active(self):
        SubjectBuilder.quickadd_ducku_duck1010()\
            .add_6month_lastyear_period()\
            .add_relatedstudents(self.testuser)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#objecttableview-table tbody tr td:nth-child(2)').alltext_normalized,
            'No')
