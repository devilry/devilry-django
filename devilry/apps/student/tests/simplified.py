from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models
from ...core import pluginloader
from ..simplified import Delivery, Feedback, Assignment, Period, Subject

import datetime


pluginloader.autodiscover()


class SimplifiedDeliveryTestCase(TestCase):

    fixtures = ['simplified/data.json']

    def setUp(self):
        self.duck1100_core = models.Subject.objects.get(short_name='duck1100')
        self.duck1100_spring01_core = models.Period.objects.get(short_name='spring01',
                                                                parentnode=self.duck1100_core)
        self.duck1100_spring01_week4_core = models.Assignment.objects.get(short_name='week4',
                                                                          parentnode=self.duck1100_spring01_core)
        ag = self.duck1100_spring01_week4_core.assignmentgroups.all()[0]
        self.duck1100_spring01_week4_deli0_core = ag.deliveries.all()[0]



class TestSimplifiedDelivery(SimplifiedDeliveryTestCase):

    def setUp(self):
        super(TestSimplifiedDelivery, self).setUp()
        self.subject_long     = 'assignment_group__parentnode__parentnode__parentnode__long_name'
        self.subject_short    = 'assignment_group__parentnode__parentnode__parentnode__short_name'
        self.subject_id       = 'assignment_group__parentnode__parentnode__parentnode__id'

        self.period_long      = 'assignment_group__parentnode__parentnode__long_name'
        self.period_short     = 'assignment_group__parentnode__parentnode__short_name'
        self.period_id        = 'assignment_group__parentnode__parentnode__id'

        self.assignment_long  = 'assignment_group__parentnode__long_name'
        self.assignment_short = 'assignment_group__parentnode__short_name'
        self.assignment_id    = 'assignment_group__parentnode__id'

    def test_search(self):

        candidate0 = User.objects.get(username='student0')

        # student0 has 11 deliveries total
        #               4 deliveries in duck1100
        #               4 deliveries in duck3580

        # check that:
        #   all deliveries are returned
        self.assertEquals(Delivery.search(candidate0).count(), 9)

        #   that a bogus search returns 0 hits
        self.assertEquals(Delivery.search(candidate0, query='this_hopefully_does_not_return_anything').count(), 0)

        #   all deliveries in subject duck1100 are returned
        self.assertEquals(Delivery.search(candidate0, query='duck1100').count(), 4)

        #   all deliveries in subject duck3580 are returned
        self.assertEquals(Delivery.search(candidate0, query='duck3580').count(), 2)

        #   all deliveries from period 'h01' are returned
        self.assertEquals(Delivery.search(candidate0, query='fall01').count(), 5)

        #   all deliveries from assignment 'week1' are returned
        self.assertEquals(Delivery.search(candidate0, query='week1').count(), 3)

    def test_read(self):

        candidate0 = User.objects.get(username='student0')
        delivery = Delivery.read(candidate0, self.duck1100_spring01_week4_deli0_core.id,
                                 ['subject', 'period', 'assignment'])

        self.assertEquals(delivery['number'], 1)
        self.assertTrue(delivery['successful'])
        # TODO: test time_of_delivery in some way
        self.assertLess(delivery['time_of_delivery'], datetime.datetime.now())

        # check subject fields
        self.assertEquals(delivery[self.subject_long], 'DUCK1100 - Getting started with python')
        self.assertEquals(delivery[self.subject_short], 'duck1100')
        self.assertEquals(delivery[self.subject_id], self.duck1100_core.id)

        # check period fields
        self.assertEquals(delivery[self.period_long], 'Spring year zero')
        self.assertEquals(delivery[self.period_short], 'spring01')
        self.assertEquals(delivery[self.period_id], self.duck1100_spring01_core.id)

        # check assigment fields
        self.assertEquals(delivery[self.assignment_long], 'The one and only week tree')
        self.assertEquals(delivery[self.assignment_short], 'week4')
        self.assertEquals(delivery[self.assignment_id], self.duck1100_spring01_week4_core.id)

    def test_read_security(self):

        candidate1 = User.objects.get(username='student1')
        examiner0  = User.objects.get(username='examiner0')
        superadmin = User.objects.get(username='grandma')

        # Check that:
        #   another student can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(candidate1, self.duck1100_spring01_week4_core.id)

        #   an examiner can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(examiner0, self.duck1100_spring01_week4_core.id)

        #   a superadmin can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(superadmin, self.duck1100_spring01_week4_core.id)


class TestSimplifiedFeedback(SimplifiedDeliveryTestCase):

    def autocreate_feedback(self, delivery, text, points=1, published=True):
        assignment = delivery.assignment_group.parentnode
        feedback = delivery.get_feedback()
        feedback.text = text
        feedback.published = published
        examiner = delivery.assignment_group.examiners.all()[0]
        feedback.last_modified_by = examiner
        gradeplugin = assignment.get_gradeplugin_registryitem().model_cls
        examplegrade = gradeplugin.get_example_xmlrpcstring(assignment,
                points)
        feedback.set_grade_from_xmlrpcstring(examplegrade)
        feedback.save()
        return feedback

    def setUp(self):
        super(TestSimplifiedFeedback, self).setUp()

        # Note: We should not depend on feedback from the fixtures, since we
        # can not predict the feedback created by the script used to generate
        # the test fixtures. So we create our own.
        for delivery in models.Delivery.objects.all():
            self.autocreate_feedback(delivery, "Hello world")
        self.feedback = self.autocreate_feedback(self.duck1100_spring01_week4_deli0_core,
                                                "This is a test")

        self.subject_long     = 'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'
        self.subject_short    = 'delivery__assignment_group__parentnode__parentnode__parentnode__short_name'
        self.subject_id       = 'delivery__assignment_group__parentnode__parentnode__parentnode__id'

        self.period_long      = 'delivery__assignment_group__parentnode__parentnode__long_name'
        self.period_short     = 'delivery__assignment_group__parentnode__parentnode__short_name'
        self.period_id        = 'delivery__assignment_group__parentnode__parentnode__id'

        self.assignment_long  = 'delivery__assignment_group__parentnode__long_name'
        self.assignment_short = 'delivery__assignment_group__parentnode__short_name'
        self.assignment_id    = 'delivery__assignment_group__parentnode__id'

        self.delivery_time    = 'delivery__time_of_delivery'
        self.delivery_number  = 'delivery__number'
        self.delivery_success = 'delivery__successful'

    def test_search(self):

        candidate0 = User.objects.get(username='student0')

        # Check that:
        #    all feedbacks are returned
        self.assertEquals(Feedback.search(candidate0).count(), 9)

        #   that a bogus search returns 0 hits
        self.assertEquals(Feedback.search(candidate0, query='this_hopefully_does_not_return_anything').count(), 0)

        #   all feedbacks in subject duck1100 are returned
        self.assertEquals(Feedback.search(candidate0, query='duck1100').count(), 4)

        #   all feedbacks in subject duck3580 are returned
        self.assertEquals(Feedback.search(candidate0, query='duck3580').count(), 2)

        #   all feedbacks from period 'h01' are returned
        self.assertEquals(Feedback.search(candidate0, query='fall01').count(), 5)

        #   all feedbacks from assignment 'week1' are returned
        self.assertEquals(Feedback.search(candidate0, query='week1').count(), 3)

    def test_read(self):

        # Grab studen0's first feedback, which has id=1
        candidate0 = User.objects.get(username='student0')
        feedback = Feedback.read(candidate0, self.feedback.id,
                                 ['subject', 'period', 'assignment', 'delivery'])

        # check feedback fields
        self.assertEquals(feedback['format'], '(\'rst\', \'ReStructured Text\')')
        self.assertEquals(feedback['text'], 'This is a test')

        # check subject fields
        self.assertEquals(feedback[self.subject_long], self.duck1100_core.long_name)
        self.assertEquals(feedback[self.subject_short], self.duck1100_core.short_name)
        self.assertEquals(feedback[self.subject_id], self.duck1100_core.id)

        # check period fields
        self.assertEquals(feedback[self.period_long], self.duck1100_spring01_core.long_name)
        self.assertEquals(feedback[self.period_short], self.duck1100_spring01_core.short_name)
        self.assertEquals(feedback[self.period_id], self.duck1100_spring01_core.id)

        # check assigment fields
        self.assertEquals(feedback[self.assignment_long], self.duck1100_spring01_week4_core.long_name)
        self.assertEquals(feedback[self.assignment_short], self.duck1100_spring01_week4_core.short_name)
        self.assertEquals(feedback[self.assignment_id], self.duck1100_spring01_week4_core.id)

        # check delivery fields
        self.assertLess(feedback[self.delivery_time], datetime.datetime.now())
        self.assertEquals(feedback[self.delivery_number], self.duck1100_spring01_week4_deli0_core.number)
        self.assertTrue(feedback[self.delivery_success])

    def test_read_security(self):

        candidate1 = User.objects.get(username='student1')
        examiner0  = User.objects.get(username='examiner0')
        superadmin = User.objects.get(username='grandma')

        # From the test data, feedback with id=1 is candidate0's first
        # feedback

        # Check that:
        #   another student can't read
        with self.assertRaises(PermissionDenied):
            Feedback.read(candidate1, self.feedback.id)

        #   an examiner can't read
        with self.assertRaises(PermissionDenied):
            Feedback.read(examiner0, self.feedback.id)

        #   a superadmin can't read
        with self.assertRaises(PermissionDenied):
            Feedback.read(superadmin, self.feedback.id)


class TestSimplifiedAssignment(SimplifiedDeliveryTestCase):
    
    # def setUp(self):
    #     self._subject_long     = 'parentnode__parentnode__parentnode__long_name'
    #     self._subject_short    = 'parentnode__parentnode__parentnode__short_name'
    #     self._subject_id       = 'parentnode__parentnode__parentnode__id'

    #     self._period_long      = 'parentnode__parentnode__long_name'
    #     self._period_short     = 'parentnode__parentnode__short_name'
    #     self._period_id        = 'parentnode__parentnode__id'

    #     self.candidate0 = User.objects.get(username="student0")
    #     self.candidate1 = User.objects.get(username="student0")

    # def test_search(self):

    #     print Assignment.search(self.candidate0)
    #     self.assertEquals(Assignment.search(self.candidate0).count(), 8)
    pass
