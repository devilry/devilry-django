from datetime import datetime
from pprint import pprint
from django.test import TestCase

from devilry_detektor.models import DetektorAssignment
from devilry_detektor.tasks import run_detektor_on_assignment
from devilry_detektor.tasks import RunDetektorOnDelivery
from devilry_detektor.tasks import FileMetasByFiletype
from devilry_detektor.tasks import FileMetaCollection
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder


class TestRunDetektorOnAssignment(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')

    def test_invalid_assignment(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            run_detektor_on_assignment.delay(
                assignment_id=200001).wait()

    def test_processing_detektorassignment_doesnotexist(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            run_detektor_on_assignment.delay(
                assignment_id=self.assignmentbuilder.assignment.id).wait()

    def test_processing_ok(self):
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)

        self.assertEquals(DetektorAssignment.objects.count(), 1)
        run_detektor_on_assignment.delay(
            assignment_id=self.assignmentbuilder.assignment.id).wait()
        self.assertEquals(DetektorAssignment.objects.count(), 1)

        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEqual(detektorassignment.processing_started_datetime, None)


class TestFileMetaCollection(TestCase):
    def setUp(self):
        self.deliverybuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()

    def test_merge_into_single_fileobject(self):
        filemeta1 = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld.java', data='test\n').filemeta
        filemeta2 = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld2.java', data='test2').filemeta
        filemetacollection = FileMetaCollection('java')
        for filemeta in filemeta1, filemeta2:
            filemetacollection.add_filemeta(filemeta)

        merged_file = filemetacollection._merge_into_single_fileobject()
        self.assertEquals(merged_file.read(), 'test\ntest2')


class TestFileMetasByFiletype(TestCase):
    def setUp(self):
        self.deliverybuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()

    def test_get_filetype_from_filename(self):
        filemetas_by_filetype = FileMetasByFiletype([])
        self.assertEquals(filemetas_by_filetype._get_filetype_from_filename('test.java'), 'java')
        self.assertEquals(filemetas_by_filetype._get_filetype_from_filename('test.py'), 'python')

    def test_group_by_extension_no_filemetas(self):
        filemetas_by_filetype = FileMetasByFiletype([])
        self.assertEquals(len(filemetas_by_filetype), 0)

    def test_group_by_extension_no_supported_files(self):
        self.deliverybuilder.add_filemeta(filename='helloworld.txt', data='Hello world')
        filemetas_by_filetype = FileMetasByFiletype([])
        self.assertEquals(len(filemetas_by_filetype), 0)

    def test_group_by_extension_has_supported_files(self):
        self.deliverybuilder.add_filemeta(filename='helloworld.txt', data='Hello world')
        helloworldpy_filemeta = self.deliverybuilder\
            .add_filemeta(filename='helloworld.py', data='def abc()').filemeta
        helloworldjava_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld.java', data='// test').filemeta
        helloworldjava2_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld2.java', data='// test2').filemeta

        # filemetas_by_filetype = RunDetektorOnDelivery(self.deliverybuilder.delivery)._group_filemetas_by_filetype()
        filemetas_by_filetype = FileMetasByFiletype(
            [helloworldpy_filemeta, helloworldjava_filemeta, helloworldjava2_filemeta])
        self.assertEquals(
            set(filemetas_by_filetype.filemetacollection_by_filetype.keys()),
            {'java', 'python'})
        self.assertEquals(
            filemetas_by_filetype['java'].size,
            len('// test') + len('// test2'))
        self.assertEquals(
            filemetas_by_filetype['python'].size,
            len('def abs()'))
        self.assertEquals(
            filemetas_by_filetype['java'].filemetas,
            [helloworldjava_filemeta, helloworldjava2_filemeta])
        self.assertEquals(
            filemetas_by_filetype['python'].filemetas,
            [helloworldpy_filemeta])

    def test_find_filetype_with_most_bytes(self):
        helloworldpy_filemeta = self.deliverybuilder\
            .add_filemeta(filename='helloworld.py', data='a').filemeta
        helloworldjava_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld.java', data='abc').filemeta
        filemetas_by_filetype = FileMetasByFiletype([helloworldpy_filemeta, helloworldjava_filemeta])
        filemetacollection = filemetas_by_filetype._find_filetype_with_most_bytes()
        self.assertEqual(filemetacollection.filetype, 'java')
        self.assertEqual(filemetacollection.filemetas, [helloworldjava_filemeta])


    # def test_get_detektor_code_signature(self):
    #     self.deliverybuilder.add_filemeta(
    #         filename='test.py',
    #         data='print "hello world"\nif a == 20: pass')
    #     code_signature = RunDetektorOnDelivery(self.deliverybuilder.delivery)\
    #         ._get_detektor_code_signature()
    #     pprint(code_signature)
    #     self.assertEqual(code_signature[''])
