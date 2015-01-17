from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
import htmls
import mock
from devilry.apps.core.models import Delivery

from devilry.devilry_student.cradmin_group import add_deliveryapp

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestAddDeliveryView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def _mock_get_request(self):
        request = self.factory.get('/test')
        request.user = self.testuser
        request.cradmin_role = self.groupbuilder.group
        request.session = mock.MagicMock()
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        return response

    def test_get(self):
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        # selector.prettyprint()

    def test_get_deadline_expired(self):
        pass

    def test_get_group_closed_expired(self):
        pass

    def test_get_no_deadlines(self):
        pass

    def _mock_post_request(self, data):
        class CustomAddDeliveryView(add_deliveryapp.AddDeliveryView):
            def get_success_url(self, delivery):
                return '/success'

        request = self.factory.post('/test', data)
        request.user = self.testuser
        request.cradmin_role = self.groupbuilder.group
        request.session = mock.MagicMock()
        response = CustomAddDeliveryView.as_view()(request)
        return response

    def test_post_single_file(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_post_request(data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1,
            'form-0-file': SimpleUploadedFile('myfile.txt', 'Hello world')
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/success')
        self.assertEqual(Delivery.objects.count(), 1)
        created_delivery = Delivery.objects.first()
        self.assertEquals(created_delivery.number, 1)
        self.assertEquals(created_delivery.delivered_by.student, self.testuser)
        self.assertEqual(created_delivery.filemetas.count(), 1)

    def test_post_multiple_files(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_post_request(data={
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 2,
            'form-0-file': SimpleUploadedFile('file1.txt', 'A'),
            'form-1-file': SimpleUploadedFile('file2.txt', 'B')
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/success')
        created_delivery = Delivery.objects.first()
        self.assertEqual(created_delivery.filemetas.count(), 2)

    def test_post_deadline_expired(self):
        pass

    def test_post_group_closed_expired(self):
        pass

    def test_post_no_deadlines(self):
        pass

    def test_post_long_filename(self):
        pass

    def test_post_duplicate_filename(self):
        pass

    def test_no_files(self):
        pass
