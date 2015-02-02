from datetime import datetime
from django.http import Http404
from django.test import TestCase, RequestFactory

from devilry.devilry_detektor.models import DetektorAssignment
from devilry.devilry_detektor.tasks import AssignmentParser
from devilry.devilry_detektor.views.admin_assignmentassembly import AssignmentAssemblyView
from devilry.devilry_detektor.comparer import CompareManyCollection
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind


class TestAssignmentAssemblyView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.assignmentbuilder = PeriodBuilder\
            .quickadd_ducku_duck1010_active()\
            .add_admins(self.testuser)\
            .add_assignment('testassignment')
        self.factory = RequestFactory()

    def test_404(self):
        request = self.factory.get('/test')
        request.user = self.testuser
        with self.assertRaises(Http404):
            AssignmentAssemblyView.as_view()(request, assignmentid=200001)

    def _create_mock_getrequest(self, data={}):
        request = self.factory.get('/test', data=data)
        request.user = self.testuser
        request.session = {}
        return request

    def test_render_first_visit(self):
        request = self._create_mock_getrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()
        self.assertNotIn('Similarity check processing was started by testuser', response.content)
        self.assertIn('Run/re-run similarity check', response.content)

    def test_processing_subsequent(self):
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)
        request = self._create_mock_getrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()
        self.assertNotIn('Similarity check processing was started by testuser', response.content)
        self.assertIn('Run/re-run similarity check', response.content)

    def test_already_running(self):
        processing_started_datetime = datetime.now()
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser,
            processing_started_datetime=processing_started_datetime,
            status='running')
        request = self._create_mock_getrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()
        self.assertIn('Similarity check processing was started by testuser', response.content)
        self.assertNotIn('Run/re-run similarity check', response.content)

    def test_results_ordering(self):
        self.assignmentbuilder\
            .add_group(name='Group A')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test1.java', data='if(i==10) {}')
        self.assignmentbuilder\
            .add_group(name='Group B')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test2.java', data='class Test {if(i==10) {}}')
        self.assignmentbuilder\
            .add_group(name='Group C')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test3.java', data='class Test {}')
        detektorassignment = DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)
        AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id).run_detektor()
        CompareManyCollection(detektorassignment).save()

        request = self._create_mock_getrequest(data={
            'language': 'java'
        })
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()

        displaynames = []
        for displayname1, displayname2 in zip(
                [span.text.strip() for span in
                 cssFind(response.content, '#detektorassembly-results .detektorassembly-delivery1-displayname')],
                [span.text.strip() for span in
                 cssFind(response.content, '#detektorassembly-results .detektorassembly-delivery2-displayname')]):
            displaynames.append({displayname1, displayname2})
        self.assertEqual(
            displaynames,
            [
                {'Group A', 'Group B'},
                {'Group A', 'Group C'},
            ])

    def _create_mock_postrequest(self):
        request = self.factory.post('/test')
        request.user = self.testuser
        request.session = {}
        return request

    def test_post(self):
        self.assertEqual(DetektorAssignment.objects.count(), 0)
        request = self._create_mock_postrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        self.assertEqual(DetektorAssignment.objects.count(), 1)
        self.assertEquals(response.status_code, 302)
        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEqual(detektorassignment.processing_started_by, self.testuser)
