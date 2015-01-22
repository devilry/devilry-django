from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.template import defaultfilters
from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.apps.core.models import Delivery, Assignment, AssignmentGroup, FileMeta
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
        request.cradmin_role = AssignmentGroup.objects.filter(id=self.groupbuilder.group.id)\
            .annotate_with_last_deadline_pk()\
            .annotate_with_last_deadline_datetime().get()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        return request

    def _mock_and_perform_get_request(self):
        request = self._mock_get_request()
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        return response

    def test_get_not_student_on_group(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.client.login(username='testuser', password='test')
        response = self.client.get(reverse('devilry_student_group-add_delivery-INDEX', kwargs={
            'roleid': self.groupbuilder.group.id,
        }))
        self.assertIn('Permission denied', response.content)

    def test_get_deadline_expired_hard_deadlines(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_deadline_expired_soft_deadlines(self):  # Soft is the default deadline_handling
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        response = self._mock_and_perform_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_add_delivery_after_soft_deadline_warning'))
        self.assertEquals(
            selector.one('#devilry_student_add_delivery_after_soft_deadline_warning p').alltext_normalized,
            'Do you really want to add a delivery after the deadline? '
            'You normally need to have a valid reason when adding deadline after the deadline.')
        self.assertEquals(
            selector.one('#devilry_student_add_delivery_after_soft_deadline_warning label').alltext_normalized,
            'I want to add a delivery after the deadline has expired.')

    def test_get_no_deadlines(self):
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_group_is_closed(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.groupbuilder.update(is_open=False)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_render(self):
        self.groupbuilder.add_students(self.testuser)
        deadline = self.groupbuilder.add_deadline_in_x_weeks(weeks=1).deadline
        response = self._mock_and_perform_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.one('.page-header h1').alltext_normalized, 'Add delivery')
        self.assertEquals(
            selector.one('#devilry_student_add_delivery_deadline_exact').alltext_normalized,
            u'({})'.format(defaultfilters.date(deadline.deadline, 'SHORT_DATETIME_FORMAT')))
        self.assertEquals(
            selector.one('#devilry_student_add_delivery_deadline_natural').alltext_normalized,
            htmls.normalize_whitespace(naturaltime(deadline.deadline)))
        self.assertFalse(selector.exists('#devilry_student_add_delivery_after_soft_deadline_warning'))

    def _mock_post_request(self, data):
        request = self.factory.post('/test', data)
        request.user = self.testuser
        request.cradmin_role = AssignmentGroup.objects.filter(id=self.groupbuilder.group.id)\
            .annotate_with_last_deadline_pk()\
            .annotate_with_last_deadline_datetime().get()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        return request

    def _mock_and_perform_post_request(self, data):
        class CustomAddDeliveryView(add_deliveryapp.AddDeliveryView):
            def get_success_url(self, delivery):
                return '/success'

        request = self._mock_post_request(data)
        response = CustomAddDeliveryView.as_view()(request)
        return response

    def test_post_single_file(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
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
        response = self._mock_and_perform_post_request(data={
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

    def test_post_no_files(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1,
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(
            selector.one('#devilry_student_add_delivery_no_files_selected_alert').alltext_normalized,
            'You have to add at least one file to make a delivery.')

    def test_post_hard_deadline_expired(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1,
            'form-0-file': SimpleUploadedFile('myfile.txt', 'Hello world')
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(
            selector.one('#devilry_student_add_delivery_hard_deadline_expired_alert').alltext_normalized,
            'The deadline has expired. Since this course is configured with hard '
            'deadlines, adding deliveries after the deadline is prohibited.')

    def test_post_soft_deadline_expired_noconfirm(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1,
            'form-0-file': SimpleUploadedFile('myfile.txt', 'Hello world')
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(
            selector.one('#devilry_student_add_delivery_soft_deadline_expired_noconfirm_alert').alltext_normalized,
            'You must confirm that you want to add a delivery after the deadline has expired.')

    def test_post_soft_deadline_expired_confirm(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1,
            'form-0-file': SimpleUploadedFile('myfile.txt', 'Hello world'),
            'confirm_delivery_after_soft_deadline': '1'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEqual(Delivery.objects.count(), 1)

    def test_post_group_closed(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.groupbuilder.update(is_open=False)
        request = self._mock_post_request(data={})
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_post_no_deadlines(self):
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_post_request(data={})
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = add_deliveryapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_post_duplicate_filename(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 2,
            'form-0-file': SimpleUploadedFile('file.txt', 'A'),
            'form-1-file': SimpleUploadedFile('file.txt', 'B')
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/success')
        self.assertEqual(Delivery.objects.count(), 1)
        delivery = Delivery.objects.first()
        self.assertEquals(delivery.filemetas.filter(filename='file.txt').count(), 1)
        self.assertEquals(delivery.filemetas.filter(filename__endswith='-file.txt').count(), 1)
