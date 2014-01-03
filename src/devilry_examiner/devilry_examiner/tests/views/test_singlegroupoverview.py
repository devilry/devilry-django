from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet


class TestSingleGroupOverview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, groupid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupid}),
                *args, **kwargs)

    def test_404_when_not_examiner(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 404)

    def test_404_when_inactive(self):
        groupbuilder = self.duck1010builder.add_6month_nextyear_period()\
            .add_assignment('week1')\
            .add_group(examiners=[self.examiner1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1],
            examiners=[self.examiner1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Week 1 &mdash; Student One')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            'duck1010, active')

    def test_deadline_render(self):
        groupbuilder = self.week1builder.add_group(
                students=[self.student1],
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1, text='This is the deadline text.')
        with self.settings(DATETIME_FORMAT='Y-m-d H:i', USE_L10N=False):
            response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertTrue(cssGet(html, '.deadlinebox h2').text.strip().startswith('Deadline 1'))
        self.assertEquals(cssGet(html, '.deadlinebox h2 .deadline-datetime').text.strip(),
            deadlinebuilder.deadline.deadline.strftime('%Y-%m-%d %H:%M'))
        self.assertEquals(cssGet(html, '.deadlinebox .deadline-text').text.strip(),
            'This is the deadline text.')

    def test_deadline_render_no_text(self):
        groupbuilder = self.week1builder.add_group(
                students=[self.student1],
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content
        self.assertEquals(len(cssFind(html, '.deadlinebox .deadline-text')), 0)