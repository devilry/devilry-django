from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models
from ...core import pluginloader
from ..simplified import Delivery, Feedback, Assignment, Period, Subject

import datetime


class SimplifiedDeliveryTestCase(TestCase):

    fixtures = ['simplified/data.json']


class TestSimplifiedDelivery(SimplifiedDeliveryTestCase):

    def setUp(self):

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
        self.assertEquals(Delivery.search(candidate0).qryset.count(), 9)

        #   that a bogus search returns 0 hits
        self.assertEquals(Delivery.search(candidate0, query='this_hopefully_does_not_return_anything').qryset.count(), 0)

        #   all deliveries in subject duck1100 are returned
        self.assertEquals(Delivery.search(candidate0, query='duck1100').qryset.count(), 4)

        #   all deliveries in subject duck3580 are returned
        self.assertEquals(Delivery.search(candidate0, query='duck3580').qryset.count(), 2)

        #   all deliveries from period 'h01' are returned
        self.assertEquals(Delivery.search(candidate0, query='fall01').qryset.count(), 5)

        #   all deliveries from assignment 'week1' are returned
        self.assertEquals(Delivery.search(candidate0, query='week1').qryset.count(), 3)

    def test_read(self):

        # Grab studen0's first delivery. 9 is the id of his first delivery
        candidate0 = User.objects.get(username='student0')
        delivery = Delivery.read(candidate0, 9, ['subject', 'period', 'assignment'])

        self.assertEquals(delivery['number'], 1)
        self.assertTrue(delivery['successful'])
        # TODO: test time_of_delivery in some way
        self.assertLess(delivery['time_of_delivery'], datetime.datetime.now())

        # check subject fields
        self.assertEquals(delivery[self.subject_long], 'DUCK1100 - Getting started with python')
        self.assertEquals(delivery[self.subject_short], 'duck1100')
        self.assertEquals(delivery[self.subject_id], 1)

        # check period fields
        self.assertEquals(delivery[self.period_long], 'Spring year zero')
        self.assertEquals(delivery[self.period_short], 'spring01')
        self.assertEquals(delivery[self.period_id], 1)

        # check assigment fields
        self.assertEquals(delivery[self.assignment_long], 'The one and only week tree')
        self.assertEquals(delivery[self.assignment_short], 'week4')
        self.assertEquals(delivery[self.assignment_id], 4)

    def test_read_security(self):

        candidate1 = User.objects.get(username='student1')
        examiner0  = User.objects.get(username='examiner0')
        superadmin = User.objects.get(username='grandma')

        # From the test data, delivery with id=9 is candidate0's first
        # delivery

        # Check that:
        #   another student can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(candidate1, 9)

        #   an examiner can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(examiner0, 9)

        #   a superadmin can't read
        with self.assertRaises(PermissionDenied):
            Delivery.read(superadmin, 9)


class TestSimplifiedFeedback(SimplifiedDeliveryTestCase):

    def setUp(self):

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
        self.assertEquals(Feedback.search(candidate0).qryset.count(), 8)

        #   that a bogus search returns 0 hits
        self.assertEquals(Feedback.search(candidate0, query='this_hopefully_does_not_return_anything').qryset.count(), 0)

        #   all feedbacks in subject duck1100 are returned
        self.assertEquals(Feedback.search(candidate0, query='duck1100').qryset.count(), 4)

        #   all feedbacks in subject duck3580 are returned
        self.assertEquals(Feedback.search(candidate0, query='duck3580').qryset.count(), 2)

        #   all feedbacks from period 'h01' are returned
        self.assertEquals(Feedback.search(candidate0, query='fall01').qryset.count(), 4)

        #   all feedbacks from assignment 'week1' are returned
        self.assertEquals(Feedback.search(candidate0, query='week1').qryset.count(), 3)

    def test_read(self):

        # Grab studen0's first feedback, which has id=1
        candidate0 = User.objects.get(username='student0')
        feedback = Feedback.read(candidate0, 1, ['subject', 'period', 'assignment', 'delivery'])

        # check feedback fields
        self.assertEquals(feedback['format'], '(\'rst\', \'ReStructured Text\')')
        self.assertEquals(feedback['text'], 'Some text here:)')

        # check subject fields
        self.assertEquals(feedback[self.subject_long], 'DUCK1100 - Getting started with python')
        self.assertEquals(feedback[self.subject_short], 'duck1100')
        self.assertEquals(feedback[self.subject_id], 1)

        # check period fields
        self.assertEquals(feedback[self.period_long], 'Spring year zero')
        self.assertEquals(feedback[self.period_short], 'spring01')
        self.assertEquals(feedback[self.period_id], 1)

        # check assigment fields
        self.assertEquals(feedback[self.assignment_long], 'The one and only week one')
        self.assertEquals(feedback[self.assignment_short], 'week1')
        self.assertEquals(feedback[self.assignment_id], 1)

        # check delivery fields
        self.assertLess(feedback[self.delivery_time], datetime.datetime.now())
        self.assertEquals(feedback[self.delivery_number], 1)
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
            Feedback.read(candidate1, 1)

        #   an examiner can't read
        with self.assertRaises(PermissionDenied):
            Feedback.read(examiner0, 1)

        #   a superadmin can't read
        with self.assertRaises(PermissionDenied):
            Feedback.read(superadmin, 1)


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

    #     print Assignment.search(self.candidate0).qryset
    #     self.assertEquals(Assignment.search(self.candidate0).qryset.count(), 8)
    pass
