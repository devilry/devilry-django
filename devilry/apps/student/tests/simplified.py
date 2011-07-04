from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models, testhelper
from ...core import pluginloader
from ..simplified import SimplifiedDelivery, SimplifiedFeedback, SimplifiedAssignment, SimplifiedPeriod, SimplifiedSubject

import datetime
import re

pluginloader.autodiscover()


class SimplifiedDeliveryTestCase(TestCase, testhelper.TestHelper):

    #fixtures = ['simplified/data.json']

    def setUp(self):
        self.load_generic_scenario()
        print self.objects_created


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
        self.assertEquals(SimplifiedDelivery.search(candidate0).count(), 9)

        #   that a bogus search returns 0 hits
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='this_hopefully_does_not_return_anything').count(), 0)

        #   all deliveries in subject duck1100 are returned
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='duck1100').count(), 4)

        #   all deliveries in subject duck3580 are returned
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='duck3580').count(), 2)

        #   all deliveries from period 'h01' are returned
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='fall01').count(), 5)

        #   all deliveries from assignment 'week1' are returned
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='fall01').count(), 5)

        #   all deliveries from assignment 'week1' are returned
        self.assertEquals(SimplifiedDelivery.search(candidate0, query='week1').count(), 3)

    def test_read(self):

        candidate0 = User.objects.get(username='student0')
        delivery = SimplifiedDelivery.read(candidate0, self.duck1100_spring01_week4_deli0_core.id,
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
            SimplifiedDelivery.read(candidate1, self.duck1100_spring01_week4_core.id)

        #   an examiner can't read
        with self.assertRaises(PermissionDenied):
            SimplifiedDelivery.read(examiner0, self.duck1100_spring01_week4_core.id)

        #   a superadmin can't read
        with self.assertRaises(PermissionDenied):
            SimplifiedDelivery.read(superadmin, self.duck1100_spring01_week4_core.id)


class TestSimplifiedFeedback(TestCase, testhelper.TestHelper):

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

        # create a base structure. Create 'examiner' as an admin, to use
        # as examiner
        self.add(nodes='uni:admin(examiner)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondSem assignments
        self.add_to_path('uni;inf101.firstSem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf101.firstSem.a2.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondSem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondSem.a2.g1:candidate(firstStud)')

        # secondStud began secondSem
        self.add_to_path('uni;inf101.secondSem.a1.g2:candidate(secondStud)')
        self.add_to_path('uni;inf101.secondSem.a2.g2:candidate(secondStud)')

        # add deliveries and feedbacks to every group that was
        # created. Default values are good enough
        for var in dir(self):
            # find any variable that ends with '_gN' where N is a
            # number
            if re.search('_g\d$', var):
                group = getattr(self, var)
                group.examiners.add(self.examiner)
                self.add_delivery(group)
                self.add_feedback(group)

    def test_search(self):

        # Check that:
        #    all feedbacks are returned
        self.assertEquals(SimplifiedFeedback.search(self.firstStud).count(), 4)

        for p in SimplifiedFeedback.search(self.firstStud):
            print p

        #   that a bogus search returns 0 hits
        self.assertEquals(SimplifiedFeedback.search(self.firstStud, query='this_hopefully_does_not_return_anything').count(), 0)

        #   all feedbacks in subject duck1100 are returned
        self.assertEquals(SimplifiedFeedback.search(self.firstStud, query='inf101').count(), 2)

        #   all feedbacks in subject duck3580 are returned
        self.assertEquals(SimplifiedFeedback.search(self.firstStud, query='inf').count(), 4)

        #   all feedbacks from period 'h01' are returned
        self.assertEquals(SimplifiedFeedback.search(self.firstStud, query='firstSem').count(), 2)

        #   all feedbacks from assignment 'week1' are returned
        self.assertEquals(SimplifiedFeedback.search(self.firstStud, query='secondSem').count(), 2)

    def test_read(self):

        # Read firstStudent's only feedback
        feedback_result = SimplifiedFeedback.read(self.firstStud, self.inf101_firstSem_a1_g1_feedbacks[-1].id,
                                           ['subject', 'period', 'assignment', 'delivery'])

        # check the feedback fields
        self.assertEquals(feedback_result['grade'], 'A')
        self.assertEquals(feedback_result['points'], 100)
        self.assertTrue(feedback_result['is_passing_grade'])

        # check subject fields
        # self.assertEquals(feedback[self.subject_long], self.duck1100_core.long_name)
        # self.assertEquals(feedback[self.subject_short], self.duck1100_core.short_name)
        # self.assertEquals(feedback[self.subject_id], self.duck1100_core.id)

        # # check period fields
        # self.assertEquals(feedback[self.period_long], self.duck1100_spring01_core.long_name)
        # self.assertEquals(feedback[self.period_short], self.duck1100_spring01_core.short_name)
        # self.assertEquals(feedback[self.period_id], self.duck1100_spring01_core.id)

        # # check assigment fields
        # self.assertEquals(feedback[self.assignment_long], self.duck1100_spring01_week4_core.long_name)
        # self.assertEquals(feedback[self.assignment_short], self.duck1100_spring01_week4_core.short_name)
        # self.assertEquals(feedback[self.assignment_id], self.duck1100_spring01_week4_core.id)

        # # check delivery fields
        # self.assertLess(feedback[self.delivery_time], datetime.datetime.now())
        # self.assertEquals(feedback[self.delivery_number], self.duck1100_spring01_week4_deli0_core.number)
        # self.assertTrue(feedback[self.delivery_success])

    def test_read_security(self):
        return
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

    def setUp(self):

        # alias the long-ass strings
        self.subject_long     = 'parentnode__parentnode__long_name'
        self.subject_short    = 'parentnode__parentnode__short_name'
        self.subject_id       = 'parentnode__parentnode__id'

        self.period_long      = 'parentnode__long_name'
        self.period_short     = 'parentnode__short_name'
        self.period_id        = 'parentnode__id'

        self.assignment_long  = 'long_name'
        self.assignment_short = 'short_name'
        self.assignment_id    = 'id'

        # create a base structure
        self.add(nodes='uni',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem'],
                 assignments=['a1', 'a2'])

        # add firstStud to the first and secondSem assignments
        self.add_to_path('uni;inf101.firstSem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf101.firstSem.a2.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondSem.a1.g1:candidate(firstStud)')
        self.add_to_path('uni;inf110.secondSem.a2.g1:candidate(firstStud)')

        # secondStud began secondSem
        self.add_to_path('uni;inf101.secondSem.a1.g2:candidate(secondStud)')
        self.add_to_path('uni;inf101.secondSem.a2.g2:candidate(secondStud)')

    def test_search(self):

        # check searches for:
        #   all
        self.assertEquals(SimplifiedAssignment.search(self.firstStud).count(), 4)

        #   subject
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='inf101').count(), 2)
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='inf110').count(), 2)

        #   period
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='firstSem').count(), 2)
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='secondSem').count(), 2)

        #   assignment
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='a1').count(), 2)
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='a2').count(), 2)

        #   some partial searches.
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='second').count(), 2)
        self.assertEquals(SimplifiedAssignment.search(self.firstStud, query='cond').count(), 2)

    def test_read(self):

        assignment_results = SimplifiedAssignment.read(self.firstStud, self.inf101_firstSem_a1.id, ['subject', 'period'])

        # check the:
        #   subject fields
        self.assertEquals(assignment_results[self.subject_long], self.inf101.long_name)
        self.assertEquals(assignment_results[self.subject_short], self.inf101.short_name)
        self.assertEquals(assignment_results[self.subject_id], self.inf101.id)

        #   period fields
        self.assertEquals(assignment_results[self.period_long], self.inf101_firstSem.long_name)
        self.assertEquals(assignment_results[self.period_short], self.inf101_firstSem.short_name)
        self.assertEquals(assignment_results[self.period_id], self.inf101_firstSem.id)

        #   assignment fields
        self.assertEquals(assignment_results[self.assignment_long], self.inf101_firstSem_a1.long_name)
        self.assertEquals(assignment_results[self.assignment_short], self.inf101_firstSem_a1.short_name)
        self.assertEquals(assignment_results[self.assignment_id], self.inf101_firstSem_a1.id)

    def test_read_security(self):

        # We know secondStud hasn't signed up for inf110. Assert that
        # he can't do a read on inf101's id
        with self.assertRaises(PermissionDenied):
            SimplifiedAssignment.read(self.secondStud, self.inf110_firstSem_a1.id)
