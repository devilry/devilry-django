from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists


class HeaderTest(object):
    def test_header(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1],
            examiners=[self.examiner1])
        assignment = self.week1builder.assignment
        response = self._getas('examiner1', assignment.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
                          'Week 1')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
                          'duck1010 &mdash; active')


class TestAllGroupsOverview(TestCase, HeaderTest):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.examiner2 = UserBuilder('examiner2').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_allgroupsoverview',
                                       kwargs={'assignmentid': assignmentid}),
                               *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1', self.week1builder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_200_when_examiner(self):
        self.week1builder.add_group(students=[self.student1],
                                    examiners=[self.examiner2])
        assignment = self.week1builder.assignment
        response = self._getas('examiner2', assignment.id)
        self.assertEquals(response.status_code, 200)

    def test_no_deadlines(self):
        self.week1builder.add_group(students=[self.student1],
                                    examiners=[self.examiner2])
        assignment = self.week1builder.assignment
        response = self._getas('examiner2', assignment.id)
        html = response.content
        deliverystatus = cssGet(html, 
                                '.infolistingtable .group .groupinfo .deliverystatus').text.strip()
        self.assertEquals(deliverystatus, 'No deadlines')

    def test_group_naming(self):
        self.week1builder.add_group(
            students=[self.student1],
            examiners=[self.examiner1])
        html = self._getas('examiner1', self.week1builder.assignment.id).content
        self.assertEquals(cssGet(html, '.infolistingtable .group .groupinfo h3 .group_long_displayname').text.strip(),
            'Student One')
        self.assertEquals(cssGet(html, '.infolistingtable .group .groupinfo h3 .group_short_displayname').text.strip(),
            '(student1)')

    def test_group_naming_anonymous(self):
        self.week1builder.update(anonymous=True)
        self.week1builder.add_group(
            students=[self.student1],
            examiners=[self.examiner1])
        html = self._getas('examiner1', self.week1builder.assignment.id).content
        self.assertEquals(
            cssGet(html, '.infolistingtable .group .groupinfo h3 .group_long_displayname').text.strip(),
            'candidate-id missing')
        self.assertFalse(cssExists(html,
            '.infolistingtable .group .groupinfo h3 .group_short_displayname'))


class TestWaitingForFeedbackOverview(TestCase, HeaderTest):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.examiner2 = UserBuilder('examiner2').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_waiting_for_feedback',
                                       kwargs={'assignmentid': assignmentid}),
                               *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1', self.week1builder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_200_when_examiner(self):
        self.week1builder.add_group(students=[self.student1],
                                    examiners=[self.examiner2])
        assignment = self.week1builder.assignment
        response = self._getas('examiner2', assignment.id)
        self.assertEquals(response.status_code, 200)


class TestWaitingForDeliveriesOverview(TestCase, HeaderTest):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.examiner2 = UserBuilder('examiner2').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_waiting_for_deliveries',
                                       kwargs={'assignmentid': assignmentid}),
                               *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1', self.week1builder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_200_when_examiner(self):
        self.week1builder.add_group(students=[self.student1],
                                    examiners=[self.examiner2])
        assignment = self.week1builder.assignment
        response = self._getas('examiner2', assignment.id)
        self.assertEquals(response.status_code, 200)


class TestCorrectedOverview(TestCase, HeaderTest):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.examiner2 = UserBuilder('examiner2').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_corrected',
                                       kwargs={'assignmentid': assignmentid}),
                               *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1', self.week1builder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_200_when_examiner(self):
        self.week1builder.add_group(students=[self.student1],
                                    examiners=[self.examiner2])
        assignment = self.week1builder.assignment
        response = self._getas('examiner2', assignment.id)
        self.assertEquals(response.status_code, 200)




class TestWaitingForFeedbackOrAllRedirectView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1').user
        self.week1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_waiting_for_feedback_or_all',
            kwargs={'assignmentid': assignmentid}), *args, **kwargs)

    def test_404_when_not_examiner(self):
        response = self._getas('examiner1', self.week1builder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_302_when_examiner(self):
        self.week1builder.add_group(examiners=[self.examiner1])
        assignment = self.week1builder.assignment
        response = self._getas('examiner1', assignment.id)
        self.assertEquals(response.status_code, 302)

    def test_no_waiting_for_feedback_examiner(self):
        self.week1builder.add_group(examiners=[self.examiner1])
        assignment = self.week1builder.assignment
        response = self._getas('examiner1', assignment.id)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.week1builder.assignment.id})))

    def test_has_waiting_for_feedback_examiner(self):
        self.week1builder.add_group(examiners=[self.examiner1])\
            .add_deadline_x_weeks_ago(weeks=1)\
            .add_delivery()
        assignment = self.week1builder.assignment
        response = self._getas('examiner1', assignment.id)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_waiting_for_feedback', kwargs={'assignmentid': self.week1builder.assignment.id})))
