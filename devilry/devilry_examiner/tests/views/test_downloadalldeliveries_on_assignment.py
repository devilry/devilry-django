from cStringIO import StringIO
import zipfile

from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_examiner.views.downloadalldeliveries_on_assignment import DownloadAllDeliveriesOnAssignmentView
from devilry.apps.core.models import Candidate


class TestDownloadAllDeliveriesOnAssignmentView(TestCase):
    def setUp(self):
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.examiner1 = UserBuilder('examiner1').user

    def _getas(self, username, assignmentid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_downloadalldeliveries_on_assignment',
            kwargs={'assignmentid': assignmentid}), *args, **kwargs)

    def test_200_as_examiner(self):
        self.assignmentbuilder.add_group(examiners=[self.examiner1])
        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        self.assertEquals(response.status_code, 200)

    def test_404_not_examiner(self):
        UserBuilder('nobody')
        self.assignmentbuilder.add_group()
        response = self._getas('nobody', self.assignmentbuilder.assignment.id)
        self.assertEquals(response.status_code, 404)

    def test_http_headers(self):
        self.assignmentbuilder.add_group(examiners=[self.examiner1])
        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        self.assertEquals(response['content-type'], 'application/zip')
        self.assertEquals(response['Content-Disposition'], 'attachment; filename=duck1010.active.assignment1.zip')

    def test_only_include_where_examiner(self):
        group1builder = self.assignmentbuilder.add_group(examiners=[self.examiner1])
        group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='helloworld.txt', data='Hello world')
        group2builder = self.assignmentbuilder.add_group(examiners=[self.examiner1])
        group2builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='test.py', data='print "test"')
        self.assignmentbuilder.add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='notincluded.txt', data='Not included')
        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        outfile = zipfile.ZipFile(StringIO(response.content), 'r')

        group1 = group1builder.group
        group2 = group2builder.group
        groupnames = [path.split('/')[1] for path in outfile.namelist()]
        self.assertEquals(set(groupnames),
                          {'1 (groupid={})'.format(group1.id), '2 (groupid={})'.format(group2.id)})

    def test_format_without_candidates(self):
        group1builder = self.assignmentbuilder.add_group(examiners=[self.examiner1])
        group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='helloworld.txt', data='Hello world')
        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        outfile = zipfile.ZipFile(StringIO(response.content), 'r')
        group1 = group1builder.group
        self.assertEquals(outfile.namelist()[0],
            'duck1010.active.assignment1/1 (groupid={groupid})/deadline-{deadline}/delivery-001/helloworld.txt'.format(
                groupid=group1.id,
                deadline=group1.last_deadline.deadline.strftime(DownloadAllDeliveriesOnAssignmentView.DEADLINE_FORMAT)
            )
        )

    def test_format_with_candidates(self):
        group1builder = self.assignmentbuilder.add_group(
            examiners=[self.examiner1],
            students=[UserBuilder('student1').user, UserBuilder('student2').user])
        group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='helloworld.txt', data='Hello world')
        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        outfile = zipfile.ZipFile(StringIO(response.content), 'r')
        group1 = group1builder.group
        groupname = outfile.namelist()[0].split('/')[1]
        self.assertEquals(groupname,
            'student1, student2 (groupid={})'.format(group1.id))

    def test_format_with_candidates_anonymous(self):
        self.assignmentbuilder.update(anonymous=True)
        group1builder = self.assignmentbuilder.add_group()\
            .add_examiners(self.examiner1)\
            .add_candidates(
                Candidate(student=UserBuilder('student1').user, candidate_id='supersecret'),
                Candidate(student=UserBuilder('student2').user))
        group1builder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='helloworld.txt', data='Hello world')

        response = self._getas('examiner1', self.assignmentbuilder.assignment.id)
        outfile = zipfile.ZipFile(StringIO(response.content), 'r')
        group1 = group1builder.group
        groupname = outfile.namelist()[0].split('/')[1]
        self.assertEquals(groupname,
            'supersecret, candidate-id missing (groupid={})'.format(group1.id))
