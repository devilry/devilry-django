from datetime import datetime
from django.http import Http404
from django.test import TestCase, RequestFactory

from devilry_detektor.models import DetektorAssignment
from devilry_detektor.tasks import AssignmentParser
from devilry_detektor.views.admin_assignmentassembly import AssignmentAssemblyView
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder


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

    def _create_mock_getrequest(self):
        request = self.factory.get('/test')
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
            processing_started_datetime=processing_started_datetime)
        request = self._create_mock_getrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()
        self.assertIn('Similarity check processing was started by testuser', response.content)
        self.assertNotIn('Run/re-run similarity check', response.content)

    def test_results_ordering(self):
        # self.assignmentbuilder\
        #     .add_group(name='Group A')\
        #     .add_deadline_in_x_weeks(weeks=1)\
        #     .add_delivery()\
        #     .add_filemeta(filename='Test.java', data='class Test {}')
        self.assignmentbuilder\
            .add_group(name='Group B')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test2.java', data='if(i==10) {}')
        self.assignmentbuilder\
            .add_group(name='Group C')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test3.java', data='class Test {if(i==10) {}}')
        self.assignmentbuilder\
            .add_group(name='Group D')\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test3.java', data='if(what == 32) {}')
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)
        AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id).run_detektor()

        request = self._create_mock_getrequest()
        response = AssignmentAssemblyView.as_view()(
            request, assignmentid=self.assignmentbuilder.assignment.id)
        response.render()
        print response.content

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
