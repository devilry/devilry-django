from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import StaticFeedback
from ..testhelper import TestHelper

class TestFeedback(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["period1:admin(teacher1)", "old_period:begins(-2):ends(1)"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)",
                                   ])
        # file and verdict
        self.goodFile = {"good.py": "print awesome"}
        self.okVerdict = {"grade": "C", "points": 85, "is_passing_grade": True}
                
        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.old_period.assignment1.g1", self.goodFile)
        
    def test_where_is_candidate(self):
        self.assertEquals(StaticFeedback.where_is_candidate(self.student1).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_candidate(self.student1).count(), 1)

    def test_published_where_is_candidate(self):
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 0)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 1)
        
        # Feedback on old period
        self.add_feedback(self.inf1100_old_period_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 1)
        
        # Set publishing time to future for period1.assignment1
        self.inf1100_period1_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_period1_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, active=False).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_candidate(self.student1, old=False).count(), 0)

    def test_where_is_examiner(self):
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_period1_assignment1_g1_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 2)

        # Create feedback on different assignmentgroup
        self.add_to_path('uio.ifi;inf1100.period1.assignment2.group1:candidate(student2):examiner(examiner1)')
        self.add_delivery("inf1100.period1.assignment2.group1", self.goodFile)
        self.add_feedback(self.inf1100_period1_assignment2_group1_deliveries[0], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.where_is_examiner(self.examiner1).count(), 3)

    def test_published_where_is_examiner(self):
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 0)
        self.add_feedback(self.inf1100_period1_assignment1_g2_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_period1_assignment1_g2_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 2)

        # Add to old period
        self.add_delivery("inf1100.old_period.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.old_period.assignment1.g2", self.goodFile)
        self.add_feedback(self.inf1100_old_period_assignment1_g2_deliveries[0], verdict=self.okVerdict)
        self.add_feedback(self.inf1100_old_period_assignment1_g2_deliveries[1], verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 4)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 2)
        
        # Create assignment2 with delivery and feedback for examiner2
        self.add_to_path('uio.ifi;inf1100.period1.assignment2.group1:candidate(student2):examiner(examiner2)')
        d = self.add_delivery("inf1100.period1.assignment2.group1", self.goodFile)
        self.add_feedback(d, verdict=self.okVerdict)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 5)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 3)
        
        # Set publishing time to future for period1.assignment1
        self.inf1100_period1_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_period1_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 3)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 2)

        # Set publishing time to future old_period.assignment1
        self.inf1100_old_period_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_old_period_assignment1.save()
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2).count(), 1)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, active=False).count(), 0)
        self.assertEquals(StaticFeedback.published_where_is_examiner(self.examiner2, old=False).count(), 1)


