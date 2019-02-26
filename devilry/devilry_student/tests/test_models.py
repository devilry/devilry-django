from os.path import exists

from django.test import TestCase
from django.core.files.base import ContentFile

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import DeliveryBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_student.models import UploadedDeliveryFile


class TestUploadedDeliveryFile(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        DeliveryBuilder.set_memory_deliverystore()

    def test_convert_to_delivery(self):
        deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1).deadline
        UploadedDeliveryFile.objects.create_with_file(
            user=self.testuser,
            deadline=deadline,
            filename='testing.txt',
            filecontent=ContentFile('Hello world')
        )
        delivery, files = UploadedDeliveryFile.objects.convert_to_delivery(deadline, self.testuser)
        self.assertIsNotNone(delivery.id)
        self.assertEqual(delivery.deadline, deadline)
        self.assertEqual(delivery.delivered_by, deadline.assignment_group.candidates.all()[0])
        self.assertEqual(delivery.delivered_by.relatedstudent.user, self.testuser)
        self.assertEqual(delivery.filemetas.count(), 1)
        filemeta = delivery.filemetas.all()[0]
        self.assertEqual(filemeta.filename, 'testing.txt')
        self.assertEqual(filemeta.get_all_data_as_string(), 'Hello world')

    def test_convert_multiple_to_delivery(self):
        deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1).deadline
        UploadedDeliveryFile.objects.create_with_file(
            user=self.testuser,
            deadline=deadline,
            filename='testing.txt',
            filecontent=ContentFile('Hello world')
        )
        UploadedDeliveryFile.objects.create_with_file(
            user=self.testuser,
            deadline=deadline,
            filename='testing2.txt',
            filecontent=ContentFile('Hello world 2')
        )
        delivery, files = UploadedDeliveryFile.objects.convert_to_delivery(deadline, self.testuser)
        self.assertEqual(delivery.filemetas.count(), 2)
        self.assertEqual(
            set([f.filename for f in delivery.filemetas.all()]),
            set(['testing.txt', 'testing2.txt']))
        self.assertEqual(
            set([f.get_all_data_as_string() for f in delivery.filemetas.all()]),
            set(['Hello world', 'Hello world 2']))


    def test_delete(self):
        deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser])\
            .add_deadline_x_weeks_ago(weeks=1).deadline
        uploadedfile = UploadedDeliveryFile.objects.create_with_file(
            user=self.testuser,
            deadline=deadline,
            filename='testing2.txt',
            filecontent=ContentFile('Hello world 2')
        )
        path = uploadedfile.uploaded_file.file.name
        self.assertTrue(exists(path))
        UploadedDeliveryFile.objects.get_queryset().all().delete_objects_and_files()
        self.assertEqual(UploadedDeliveryFile.objects.count(), 0)
        self.assertFalse(exists(path))


    def test_prepare_filename(self):
        self.assertEqual(UploadedDeliveryFile.prepare_filename('test.txt'), 'test.txt')
        self.assertEqual(255,
            len(UploadedDeliveryFile.prepare_filename('x'*300)))
        self.assertEqual(
            UploadedDeliveryFile.prepare_filename('{}yy.txt'.format('x'*251)),
            '{}.txt'.format('x'*251))
