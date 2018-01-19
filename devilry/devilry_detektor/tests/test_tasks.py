from django.test import TestCase

from devilry.devilry_detektor.models import DetektorAssignment
from devilry.devilry_detektor.models import DetektorDeliveryParseResult
from devilry.devilry_detektor.tasks import DeliveryParser
from devilry.devilry_detektor.tasks import AssignmentParser
from devilry.devilry_detektor.tasks import FileMetasByFiletype
from devilry.devilry_detektor.tasks import FileMetaCollection
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder


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

    def test_get_language_from_filename(self):
        filemetas_by_language = FileMetasByFiletype([])
        self.assertEquals(filemetas_by_language._get_language_from_filename('test.java'), 'java')
        self.assertEquals(filemetas_by_language._get_language_from_filename('test.py'), 'python')

    def test_group_by_extension_no_filemetas(self):
        filemetas_by_language = FileMetasByFiletype([])
        self.assertEquals(len(filemetas_by_language), 0)

    def test_group_by_extension_no_supported_files(self):
        self.deliverybuilder.add_filemeta(filename='helloworld.txt', data='Hello world')
        filemetas_by_language = FileMetasByFiletype([])
        self.assertEquals(len(filemetas_by_language), 0)

    def test_group_by_extension_has_supported_files(self):
        self.deliverybuilder.add_filemeta(filename='helloworld.txt', data='Hello world')
        helloworldpy_filemeta = self.deliverybuilder\
            .add_filemeta(filename='helloworld.py', data='def abc()').filemeta
        helloworldjava_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld.java', data='// test').filemeta
        helloworldjava2_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld2.java', data='// test2').filemeta

        # filemetas_by_language = DeliveryParser(self.deliverybuilder.delivery)._group_filemetas_by_language()
        filemetas_by_language = FileMetasByFiletype(
            [helloworldpy_filemeta, helloworldjava_filemeta, helloworldjava2_filemeta])
        self.assertEquals(
            set(filemetas_by_language.filemetacollection_by_language.keys()),
            {'java', 'python'})
        self.assertEquals(
            filemetas_by_language['java'].size,
            len('// test') + len('// test2'))
        self.assertEquals(
            filemetas_by_language['python'].size,
            len('def abs()'))
        self.assertEquals(
            filemetas_by_language['java'].filemetas,
            [helloworldjava_filemeta, helloworldjava2_filemeta])
        self.assertEquals(
            filemetas_by_language['python'].filemetas,
            [helloworldpy_filemeta])

    def test_find_language_with_most_bytes(self):
        helloworldpy_filemeta = self.deliverybuilder\
            .add_filemeta(filename='helloworld.py', data='a').filemeta
        helloworldjava_filemeta = self.deliverybuilder\
            .add_filemeta(filename='HelloWorld.java', data='abc').filemeta
        filemetas_by_language = FileMetasByFiletype([helloworldpy_filemeta, helloworldjava_filemeta])
        filemetacollection = filemetas_by_language.find_language_with_most_bytes()
        self.assertEqual(filemetacollection.language, 'java')
        self.assertEqual(filemetacollection.filemetas, [helloworldjava_filemeta])


class TestDeliveryParser(TestCase):
    def setUp(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')
        self.deliverybuilder = assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        DetektorAssignment.objects.create(
            assignment=assignmentbuilder.assignment)
        self.assignmentparser = AssignmentParser(assignmentbuilder.assignment.id)

    def test_no_filemetas(self):
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 0)
        deliveryparser = DeliveryParser(self.assignmentparser, self.deliverybuilder.delivery)
        deliveryparser.run_detektor()
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 0)

    def test_single_language_single_file(self):
        self.deliverybuilder.add_filemeta(filename='Test.java', data='class Test {}')
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 0)
        deliveryparser = DeliveryParser(self.assignmentparser, self.deliverybuilder.delivery)
        deliveryparser.run_detektor()
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 1)
        parseresult = DetektorDeliveryParseResult.objects.all()[0]
        self.assertEquals(parseresult.get_operators_and_keywords_string(), 'class')
        self.assertEquals(parseresult.get_number_of_keywords(), 1)
        self.assertEquals(parseresult.get_number_of_operators(), 0)

    def test_single_language_multiple_files(self):
        self.deliverybuilder.add_filemeta(filename='Test.java', data='class Test {}')
        self.deliverybuilder.add_filemeta(filename='AnotherTest.java', data='if(i==10){}')
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 0)
        deliveryparser = DeliveryParser(self.assignmentparser, self.deliverybuilder.delivery)
        deliveryparser.run_detektor()
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 1)
        parseresult = DetektorDeliveryParseResult.objects.all()[0]
        self.assertEquals(parseresult.get_operators_and_keywords_string(), 'if==class')
        self.assertEquals(parseresult.get_number_of_keywords(), 2)
        self.assertEquals(parseresult.get_number_of_operators(), 1)

    def test_multiple_languages(self):
        self.deliverybuilder.add_filemeta(filename='Test.java', data='class Test {}')
        self.deliverybuilder.add_filemeta(filename='test.py', data='class Test: pass')
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 0)
        deliveryparser = DeliveryParser(self.assignmentparser, self.deliverybuilder.delivery)
        deliveryparser.run_detektor()
        self.assertEquals(DetektorDeliveryParseResult.objects.count(), 2)
        parseresults = DetektorDeliveryParseResult.objects.order_by('language')
        parseresult_java = parseresults[0]
        parseresult_python = parseresults[1]
        self.assertEquals(parseresult_java.get_operators_and_keywords_string(), 'class')
        self.assertEquals(parseresult_java.get_number_of_keywords(), 1)
        self.assertEquals(parseresult_java.get_number_of_operators(), 0)
        self.assertEquals(parseresult_python.get_operators_and_keywords_string(), 'classpass')
        self.assertEquals(parseresult_python.get_number_of_keywords(), 2)
        self.assertEquals(parseresult_python.get_number_of_operators(), 0)


class TestAssignmentParser(TestCase):
    # def setUp(self):
    #     assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_assignment('testassignment')
    #     self.deliverybuilder = assignmentbuilder\
    #         .add_group()\
    #         .add_deadline_in_x_weeks(weeks=1)\
    #         .add_delivery()
    #     DetektorAssignment.objects.create(
    #         assignment=assignmentbuilder.assignment)
    #     self.assignmentparser = AssignmentParser(assignmentbuilder.assignment.id)


    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')

    def test_invalid_assignment(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            AssignmentParser(assignment_id=200001)

    def test_processing_detektorassignment_doesnotexist(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id)

    def test_processing_ok_no_deliveries(self):
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)
        AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id).run_detektor()
        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEquals(detektorassignment.parseresults.count(), 0)

    def test_processing_ok_has_deliveries(self):
        self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test.java', data='class Test {}')
        self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_filemeta(filename='Test2.java', data='if(i==10) {}')

        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)
        AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id).run_detektor()

        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEquals(detektorassignment.parseresults.count(), 2)
        parseresults = detektorassignment.parseresults.order_by('number_of_operators')
        self.assertEquals(parseresults[0].get_operators_and_keywords_string(), 'class')
        self.assertEquals(parseresults[1].get_operators_and_keywords_string(), 'if==')

    def test_get_unprocessed_delivery_queryset_none(self):
        delivery1builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery1builder.add_filemeta(filename='Test.java', data='class Test {}')
        delivery2builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery2builder.add_filemeta(filename='Test2.java', data='if(i==10) {}')

        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)

        assignmentparser = AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id)
        DeliveryParser(assignmentparser, delivery1builder.delivery).run_detektor()
        DeliveryParser(assignmentparser, delivery2builder.delivery).run_detektor()
        self.assertEqual(assignmentparser.get_unprocessed_delivery_queryset().count(), 0)

    def test_get_unprocessed_delivery_queryset_some(self):
        delivery1builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery1builder.add_filemeta(filename='Test.java', data='class Test {}')
        delivery2builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery2builder.add_filemeta(filename='Test2.java', data='if(i==10) {}')

        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)

        assignmentparser = AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id)
        DeliveryParser(assignmentparser, delivery1builder.delivery).run_detektor()
        self.assertEqual(assignmentparser.get_unprocessed_delivery_queryset().count(), 1)
        self.assertEqual(
            assignmentparser.get_unprocessed_delivery_queryset().all()[0],
            delivery2builder.delivery)

    def test_processing_ok_has_all_previous_results(self):
        delivery1builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery1builder.add_filemeta(filename='Test.java', data='class Test {}')
        delivery2builder = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()
        delivery2builder.add_filemeta(filename='Test2.java', data='if(i==10) {}')

        detektorassignment = DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)

        assignmentparser = AssignmentParser(assignment_id=self.assignmentbuilder.assignment.id)
        self.assertEquals(detektorassignment.parseresults.count(), 0)
        DeliveryParser(assignmentparser, delivery1builder.delivery).run_detektor()
        self.assertEquals(detektorassignment.parseresults.count(), 1)
        assignmentparser.run_detektor()
        self.assertEquals(detektorassignment.parseresults.count(), 2)
