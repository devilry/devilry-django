from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from ..models import Delivery, AssignmentGroup
from ..testhelper import TestHelper

class TestDelivery(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["period1:admin(teacher1)"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:candidate(student2):examiner(examiner2)",
                                   "g3:candidate(student3,student2):examiner(examiner1,examiner2,examiner3)",
                                   "g4:candidate(student4):examiner(examiner3)"])
        self.goodFile = {"good.py": "print awesome"}
        self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 3)

    def test_delivery(self):
        assignmentgroup = self.inf1100_period1_assignment1_g3
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)
        self.assertEquals(d.deadline.assignment_group, assignmentgroup)
        #self.assertEquals(d.assignment_group, assignmentgroup)
        #self.assertTrue(d.successful)
        #self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 2)

        # TODO find a graceful way to handle this error:
        d.number = 1
        self.assertRaises(IntegrityError, d.save())

    def test_published_where_is_candidate(self):
        # Add 2 on g1
        d = self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g1", self.goodFile)
        # Add 3 on g2
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g2", self.goodFile)
        # Add 2 on g3
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)
        d = self.add_delivery("inf1100.period1.assignment1.g3", self.goodFile)

        self.assertEquals(Delivery.published_where_is_candidate(self.student1).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student2).count(), 7)
        self.assertEquals(Delivery.published_where_is_candidate(self.student3).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student4).count(), 0)
