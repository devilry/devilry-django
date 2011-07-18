from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Delivery, Deadline
from ..testhelper import TestHelper

TestHelper.set_memory_deliverystore()

class TestDeadline(TestCase, TestHelper):

    def setUp(self):
        self.goodFile = {"good.py": "print awesome"}
        self.okVerdict = {"grade": "C", "points": 85, "is_passing_grade": True}

    def test_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1)')
        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)        
        # ..._assignment1.examiners_publish_feedbacks_directly is True by default
        self.assertTrue(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)

    def test_dont_publish_feedbacks_directly(self):
        self.add_to_path('uio.ifi;inf1100.period1.assignment1.group1:candidate(student1):examiner(examiner1)')
        # Disable publish feedbacks directly before adding delivery and feedback
        self.inf1100_period1_assignment1.examiners_publish_feedbacks_directly = False
        self.inf1100_period1_assignment1.save()

        self.delivery = self.add_delivery("inf1100.period1.assignment1.group1", self.goodFile)
        self.feedback = self.add_feedback(self.delivery, verdict=self.okVerdict)        
        self.assertFalse(Deadline.objects.get(id=self.feedback.delivery.deadline.id).feedbacks_published)
