from datetime import datetime
from django.core import mail

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFile
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
import mock

from devilry.devilry_student.cradmin_group import deliveriesapp
from devilry.apps.core.models import Delivery, Assignment, AssignmentGroup, Candidate, deliverytypes
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestDeliveryListView(TestCase):
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
        request.cradmin_app = mock.MagicMock()
        request.session = mock.MagicMock()
        response = deliveriesapp.DeliveryListView.as_view()(request)
        return response

    def test_list_no_deliveries(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#objecttableview-table'))
        self.assertFalse(selector.exists('#objecttableview-table tbody tr'))

    def test_list_has_deliveries(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 2)

    def test_list_exclude_electronic_deliveries_without_feedback(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(
            hours=1, delivery_type=deliverytypes.NON_ELECTRONIC)
        deadlinebuilder\
            .add_delivery_x_hours_before_deadline(hours=2, delivery_type=deliverytypes.NON_ELECTRONIC)\
            .add_passed_A_feedback(saved_by=UserBuilder('testexaminer').user)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)

    def test_render_no_feedback(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('.devilry-student-delivery-summarycolumn-feedback'))
        self.assertTrue(selector.exists('.devilry-student-delivery-summarycolumn-no-feedback'))
        self.assertEquals(
            selector.one('.devilry-student-delivery-summarycolumn-no-feedback').alltext_normalized,
            'No feedback')

    def test_render_has_feedback(self):
        deadlinebuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        delivery = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=26)
        delivery.add_feedback(
            points=10,
            grade='Good',
            is_passing_grade=True,
            saved_by=self.testuser)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('.devilry-student-delivery-summarycolumn-no-feedback'))

        self.assertTrue(selector.exists('.devilry-student-delivery-summarycolumn-feedback'))
        self.assertTrue(selector.exists('.devilry-student-delivery-summarycolumn-feedback-grade'))
        self.assertTrue(selector.exists('.devilry-student-delivery-summarycolumn-feedback-is_passing_grade'))
        self.assertEquals(
            selector.one('.devilry-student-delivery-summarycolumn-feedback-grade').alltext_normalized,
            'Good')
        self.assertEquals(
            selector.one('.devilry-student-delivery-summarycolumn-feedback-is_passing_grade').alltext_normalized,
            'passed')


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
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        return response

    def test_get_not_student_on_group(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.client.login(username='testuser', password='test')
        response = self.client.get(reverse('devilry_student_group-deliveries-INDEX', kwargs={
            'roleid': self.groupbuilder.group.id,
        }))
        self.assertIn('Permission denied', response.content)

    def test_get_deadline_expired_hard_deadlines(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_deadline_expired_soft_deadlines(self):  # Soft is the default deadline_handling
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        response = self._mock_and_perform_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#div_id_confirm_delivery_after_soft_deadline'))
        self.assertIn(
            'Do you really want to add a delivery after the deadline? '
            'You normally need to have a valid reason when adding a delivery after the deadline.',
            selector.one('#devilry_student_add_delivery_form').alltext_normalized,)

    def test_get_no_deadlines(self):
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_group_is_closed(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        self.groupbuilder.update(is_open=False)
        request = self._mock_get_request()
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_get_no_deadlinemessage(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_add_delivery_deadlinemessage_wrapper'))

    def test_get_empty_deadlinemessage(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1, text='    ')
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_add_delivery_deadlinemessage_wrapper'))

    def test_get_has_deadlinemessage(self):
        self.groupbuilder.add_deadline_in_x_weeks(
            weeks=1, text='A testmessage')
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_get_request()
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_add_delivery_deadlinemessage_wrapper'))
        self.assertEquals(
            selector.one('#devilry_student_add_delivery_deadlinemessage').text,
            'A testmessage')

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
        class CustomAddDeliveryView(deliveriesapp.AddDeliveryView):
            def get_success_url(self, delivery):
                return '/success'

        request = self._mock_post_request(data)
        response = CustomAddDeliveryView.as_view()(request)
        return response

    def _create_collection(self, user, files, **kwargs):
        collection = TemporaryFileCollection.objects.create(
            user=user, **kwargs)
        for filename, filecontent in files:
            temporaryfile = TemporaryFile(
                collection=collection,
                filename=filename)
            temporaryfile.file.save(filename, ContentFile(filecontent))
        return collection

    def test_post_single_file(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[
            ('testfile.txt', 'Testcontent')])

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/success')
        self.assertEqual(Delivery.objects.count(), 1)
        created_delivery = Delivery.objects.first()
        self.assertEquals(created_delivery.number, 1)
        self.assertEquals(created_delivery.delivered_by.student, self.testuser)
        self.assertEqual(created_delivery.filemetas.count(), 1)
        self.assertEqual(created_delivery.filemetas.first().get_all_data_as_string(), 'Testcontent')

    def test_post_multiple_files(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[
            ('testfile1.txt', 'Testcontent1'),
            ('testfile2.txt', 'Testcontent2')])

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/success')
        created_delivery = Delivery.objects.first()
        self.assertEqual(created_delivery.filemetas.count(), 2)
        self.assertEquals(
            created_delivery.filemetas.get(filename='testfile1.txt').get_all_data_as_string(),
            'Testcontent1')
        self.assertEquals(
            created_delivery.filemetas.get(filename='testfile2.txt').get_all_data_as_string(),
            'Testcontent2')

    def test_post_no_files(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[])

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#div_id_filecollectionid.has-error'))
        self.assertIn(
            'You have to add at least one file to make a delivery.',
            selector.one('#div_id_filecollectionid').alltext_normalized)

    def test_post_no_collectionid(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#div_id_filecollectionid.has-error'))
        self.assertIn(
            'You have to add at least one file to make a delivery.',
            selector.one('#div_id_filecollectionid').alltext_normalized)

    def test_post_hard_deadline_expired(self):
        self.assignmentbuilder.update(deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={})
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
        response = self._mock_and_perform_post_request(data={})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Delivery.objects.count(), 0)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#div_id_confirm_delivery_after_soft_deadline.has-error'))
        self.assertIn(
            'You must confirm that you want to add a delivery after the deadline has expired.',
            selector.one('#div_id_confirm_delivery_after_soft_deadline').alltext_normalized)

    def test_post_soft_deadline_expired_confirm(self):
        self.groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[
            ('testfile.txt', 'Testcontent')])

        self.assertEqual(Delivery.objects.count(), 0)
        response = self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id,
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
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_post_no_deadlines(self):
        self.groupbuilder.add_students(self.testuser)
        request = self._mock_post_request(data={})
        request.cradmin_instance.appindex_url.return_value = '/appindex_url_called'
        response = deliveriesapp.AddDeliveryView.as_view()(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], '/appindex_url_called')
        request.cradmin_instance.appindex_url.assert_called_with('deliveries')

    def test_post_successfully_deletes_collection(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[
            ('testfile.txt', 'Testcontent')])

        response = self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id
        })
        self.assertEquals(response.status_code, 302)
        self.assertFalse(TemporaryFileCollection.objects.filter(id=collection.id).exists())

    def test_post_successfully_sends_email(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)
        collection = self._create_collection(user=self.testuser, files=[
            ('testfile.txt', 'Testcontent')])

        self.assertEqual(len(mail.outbox), 0)
        self._mock_and_perform_post_request(data={
            'filecollectionid': collection.id
        })
        self.assertEqual(len(mail.outbox), 1)


class TestDeliveryDetailsView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def _get_as(self, username, deliveryid):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='deliveries',
            roleid=self.groupbuilder.group.id,
            viewname='deliverydetails',
            kwargs={'pk': deliveryid}))

    def test_delivery_metadata_no_files(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_files_title'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_files'))

    def test_delivery_metadata_files(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10)
        deliverybuilder.add_filemeta(filename='test1.txt', data='testdata')
        deliverybuilder.add_filemeta(filename='test2.txt', data='testdata')

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_files_title'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_files'))
        self.assertEquals(selector.count('#devilry_student_group_deliverydetails_files a'), 2)
        self.assertEquals(
            [element.alltext_normalized
             for element in selector.list('#devilry_student_group_deliverydetails_files a')],
            ['test1.txt', 'test2.txt'])

    def test_delivery_metadata_file_urls(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10)
        filemeta = deliverybuilder.add_filemeta(filename='test1.txt', data='testdata').filemeta

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#devilry_student_group_deliverydetails_files a'), 1)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_files a')['href'],
            reverse('devilry-delivery-file-download', kwargs={'filemetaid': filemeta.id}))

    def test_delivery_metadata_delivered_by(self):
        self.groupbuilder.add_students(self.testuser)
        candidate = Candidate.objects.create(
            student=UserBuilder('someuser', full_name='Some User').user,
            assignment_group=self.groupbuilder.group)
        self.groupbuilder.add_candidates(candidate)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(
                hours=10, delivered_by=candidate)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_delivered_by').alltext_normalized,
            'Some User')

    def test_delivery_metadata_delivered_by_none(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(
                hours=10, delivered_by=None)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_delivered_by'))

    def test_delivery_metadata_time_of_delivery(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery(time_of_delivery=datetime(2000, 1, 1, 12, 30))

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_time_of_delivery').alltext_normalized,
            'January 1, 2000, 12:30')

    def test_delivery_metadata_time_of_delivery_after_deadline(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_after_deadline(hours=2)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertIn(
            'After the deadline',
            selector.one('#devilry_student_group_deliverydetails_time_of_delivery').alltext_normalized)

    def test_delivery_metadata_delivery(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder\
            .add_deadline(deadline=datetime(2004, 1, 1, 12, 30))\
            .add_delivery_x_hours_before_deadline(hours=1)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_deadline').alltext_normalized,
            'January 1, 2004, 12:30')

    def test_delivery_metadata_feedback_written_by(self):
        self.groupbuilder.add_students(self.testuser)
        testexaminer = UserBuilder('testexaminer', full_name='Test Examiner').user
        self.groupbuilder.add_examiners(testexaminer)
        deliverybuilder = self.groupbuilder\
            .add_deadline(deadline=datetime(2004, 1, 1, 12, 30))\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_passed_A_feedback(saved_by=testexaminer)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_feedback_written_by').alltext_normalized,
            'Test Examiner')

    def test_delivery_metadata_feedback_written_by_anonymous(self):
        self.assignmentbuilder.update(anonymous=True)
        self.groupbuilder.add_students(self.testuser)
        testexaminer = UserBuilder('testexaminer', full_name='Test Examiner').user
        self.groupbuilder.add_examiners(testexaminer)
        deliverybuilder = self.groupbuilder\
            .add_deadline(deadline=datetime(2004, 1, 1, 12, 30))\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_passed_A_feedback(saved_by=testexaminer)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_feedback_written_by'))

    def test_delivery_metadata_feedback_save_timestamp(self):
        self.groupbuilder.add_students(self.testuser)
        testexaminer = UserBuilder('testexaminer', full_name='Test Examiner').user
        self.groupbuilder.add_examiners(testexaminer)
        deliverybuilder = self.groupbuilder\
            .add_deadline(deadline=datetime(2004, 1, 1, 12, 30))\
            .add_delivery_x_hours_before_deadline(hours=1)
        feedback = deliverybuilder.add_passed_A_feedback(saved_by=testexaminer).feedback
        feedback.save_timestamp = datetime(2004, 2, 1, 12, 30)
        feedback.save(autoset_timestamp_to_now=False)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_feedback_save_timestamp').alltext_normalized,
            'February 1, 2004, 12:30')

    def test_delivery_metadata_no_time_of_delivery_or_deadline_or_deliveredby_for_nonelectronic(self):
        self.groupbuilder.add_students(self.testuser)
        candidate = Candidate.objects.create(student=self.testuser, assignment_group=self.groupbuilder.group)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1, delivered_by=candidate,
                                                  delivery_type=deliverytypes.NON_ELECTRONIC)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_delivered_by_title'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_delivered_by'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_time_of_delivery_title'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_time_of_delivery'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_deadline_title'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_deadline'))

    def test_delivery_metadata_has_time_of_delivery_and_deadline_and_deliveredby_for_electronic(self):
        self.assignmentbuilder.update(delivery_types=deliverytypes.ELECTRONIC)
        self.groupbuilder.add_students(self.testuser)
        candidate = Candidate.objects.create(student=self.testuser, assignment_group=self.groupbuilder.group)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1, delivered_by=candidate)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_delivered_by_title'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_delivered_by'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_time_of_delivery_title'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_time_of_delivery'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_deadline_title'))
        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_deadline'))

    def test_anonymous_sanity(self):
        self.assignmentbuilder.update(anonymous=True)
        self.groupbuilder.add_students(self.testuser)
        testexaminer1 = UserBuilder('testexaminer1').user
        self.groupbuilder.add_examiners(
            testexaminer1,
            UserBuilder('testexaminer2', 'Test Examiner').user)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10, delivered_by=None)
        deliverybuilder.add_passed_A_feedback(saved_by=testexaminer1)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        self.assertNotIn('testexaminer1', response.content)
        self.assertNotIn('testexaminer2', response.content)
        self.assertNotIn('Test Examiner', response.content)

    def test_no_feedback(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_feedback_summary'))
        self.assertFalse(selector.exists('#devilry_student_group_deliverydetails_feedback'))

    def test_feedback_summary_passed(self):
        self.groupbuilder.add_students(self.testuser)
        testexaminer = UserBuilder('testexaminer').user
        self.groupbuilder.add_examiners(testexaminer)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10, delivered_by=None)
        deliverybuilder.add_feedback(saved_by=testexaminer,
                                     grade='10/20',
                                     is_passing_grade=True,
                                     points=20)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('.devilry-student-deliverydetails-feedbacksummary-passed'))
        self.assertTrue(selector.exists(
            '.django-cradmin-container-fluid-focus.django-cradmin-container-fluid-focus-success'))
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_feedback_summary').alltext_normalized,
            'This delivery has been corrected, and the grade is: 10/20 (passed)')

    def test_feedback_summary_failed(self):
        self.groupbuilder.add_students(self.testuser)
        testexaminer = UserBuilder('testexaminer1').user
        self.groupbuilder.add_examiners(testexaminer)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10, delivered_by=None)
        deliverybuilder.add_feedback(saved_by=testexaminer,
                                     grade='2/20',
                                     is_passing_grade=False,
                                     points=2)

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)

        self.assertTrue(selector.exists('.devilry-student-deliverydetails-feedbacksummary-failed'))
        self.assertTrue(selector.exists
                        ('.django-cradmin-container-fluid-focus.django-cradmin-container-fluid-focus-warning'))
        self.assertEquals(
            selector.one('#devilry_student_group_deliverydetails_feedback_summary').alltext_normalized,
            'This delivery has been corrected, and the grade is: 2/20 (failed)')

    def test_feedback_rendered_view(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10, delivered_by=None)
        deliverybuilder.add_passed_A_feedback(
            saved_by=UserBuilder('testexaminer1').user,
            rendered_view='<p>This is a test</p>')

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)

        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_feedback_rendered_view'))
        self.assertEqual(
            selector.one('#devilry_student_group_deliverydetails_feedback_rendered_view').alltext_normalized,
            'This is a test')
        self.assertEqual(  # Ensure we do not strip html
            selector.count('#devilry_student_group_deliverydetails_feedback_rendered_view p'),
            1)

    def test_feedback_rendered_view_fileattachments(self):
        self.groupbuilder.add_students(self.testuser)
        deliverybuilder = self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=10, delivered_by=None)
        deliverybuilder\
            .add_passed_A_feedback(saved_by=UserBuilder('testexaminer1').user,
                                   rendered_view='')\
            .add_fileattachment(filename='testfile.txt')

        response = self._get_as('testuser', deliverybuilder.delivery.id)
        response.render()
        selector = htmls.S(response.content)

        self.assertTrue(selector.exists('#devilry_student_group_deliverydetails_feedback_rendered_view'))
        self.assertTrue(selector.exists('ul.devilry-feedback-rendered-view-files'))
        self.assertEqual(selector.count('ul.devilry-feedback-rendered-view-files li'), 1)
        self.assertEqual(
            selector.one('ul.devilry-feedback-rendered-view-files li').alltext_normalized,
            'testfile.txt')
