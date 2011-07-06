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
        self.inf1100_period1_assignment1_g1.deliveries.create(delivered_by=self.student1, successful=False)
        self.inf1100_period1_assignment1_g2.deliveries.create(delivered_by=self.student2, successful=False)
        self.inf1100_period1_assignment1_g3.deliveries.create(delivered_by=self.student3, successful=False)

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 3)

    def test_delivery(self):
        assignmentgroup = self.inf1100_period1_assignment1_g3
        d = assignmentgroup.deliveries.create(delivered_by=self.student1, successful=False)
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertFalse(d.successful)
        d.successful = True
        d.save()
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 2)

        d2 = assignmentgroup.deliveries.create(delivered_by=self.student1, successful=True)
        self.assertTrue(d2.successful)
        self.assertEquals(d2.number, 3)
        d2.save()

        # TODO find a graceful way to handle this error:
        d2.number = 2
        self.assertRaises(IntegrityError, d2.save)

    def test_published_where_is_candidate(self):
        # Add 2 on g1
        self.inf1100_period1_assignment1_g1.deliveries.create(delivered_by=self.student1, successful=False)
        self.inf1100_period1_assignment1_g1.deliveries.create(delivered_by=self.student1, successful=False)
        # Add 3 on g2
        self.inf1100_period1_assignment1_g2.deliveries.create(delivered_by=self.student2, successful=False)
        self.inf1100_period1_assignment1_g2.deliveries.create(delivered_by=self.student2, successful=False)
        self.inf1100_period1_assignment1_g2.deliveries.create(delivered_by=self.student2, successful=False)
        # Add 2 on g3
        self.inf1100_period1_assignment1_g3.deliveries.create(delivered_by=self.student3, successful=False)
        self.inf1100_period1_assignment1_g3.deliveries.create(delivered_by=self.student3, successful=False)
        
        self.assertEquals(Delivery.published_where_is_candidate(self.student1).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student2).count(), 7)
        self.assertEquals(Delivery.published_where_is_candidate(self.student3).count(), 3)
        self.assertEquals(Delivery.published_where_is_candidate(self.student4).count(), 0)
