from django.core.exceptions import ValidationError
from datetime import timedelta
from django.test import TestCase

from ..models import Deadline
from ..testhelper import TestHelper

TestHelper.set_memory_deliverystore()

class TestDeadline(TestCase, TestHelper):

    def setUp(self):
        self.goodFile = {"good.py": "print awesome"}
        self.okVerdict = {"grade": "C", "points": 85, "is_passing_grade": True}

    def test_create_new_groupclose(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1')
        group = self.inf1100_period1_assignment1_group1
        group.is_open = False
        group.save()
        self.assertFalse(group.is_open)
        deadline = group.deadlines.create(deadline=group.parentnode.parentnode.start_time + timedelta(0, 10))
        self.assertTrue(group.is_open)

    def test_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1).d1:ends(10)')
        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)        
        # ..._assignment1.examiners_publish_feedbacks_directly is True by default
        self.assertTrue(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)

    def test_dont_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1).d1:ends(10)')
        # Disable publish feedbacks directly before adding delivery and feedback
        self.inf1100_period1_assignment1.examiners_publish_feedbacks_directly = False
        self.inf1100_period1_assignment1.save()

        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)        
        self.assertFalse(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)

    def test_deadline_notunique(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1.g1.d1:ends(5)')
        self.add_to_path('uni;sub.p1.a1.g2.d1:ends(5)')

        g1 = self.sub_p1_a1_g1
        d1 = self.sub_p1_a1_g1_d1
        g2_d1 = self.sub_p1_a1_g2_d1

        # Ensure that we are not checking outside the group (the tests below would fail if this fails)
        self.assertEquals(d1.deadline, g2_d1.deadline)

        # Will not fail because id matches in the validator
        d1.full_clean()

        d2 = Deadline(assignment_group=g1, deadline=d1.deadline)
        with self.assertRaises(ValidationError):
            d2.full_clean()
