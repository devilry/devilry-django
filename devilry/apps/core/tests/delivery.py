from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from ..models import Delivery, AssignmentGroup

class TestDelivery(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Delivery.where_is_admin(teacher1).count(), 3)

    def test_delivery(self):
        student1 = User.objects.get(username='student1')
        assignmentgroup = AssignmentGroup.objects.get(id=1)
        d = assignmentgroup.deliveries.create(delivered_by=student1,
                                              successful=False)
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertFalse(d.successful)
        d.successful = True
        d.save()
        self.assertEquals(d.assignment_group, assignmentgroup)
        self.assertTrue(d.successful)
        self.assertEquals(d.number, 3)

        d2 = assignmentgroup.deliveries.create(delivered_by=student1,
                                               successful=True)
        self.assertTrue(d2.successful)
        self.assertEquals(d2.number, 4)
        d2.save()

        # TODO find a graceful way to handle this error:
        d2.number = 3
        self.assertRaises(IntegrityError, d2.save)

    def test_published_where_is_candidate(self):
        student1 = User.objects.get(username='student1')
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        student4 = User.objects.get(username='student4')

        # In the fixtures, student1 has 2 deliveries
        #                  student2 has 1 delivery
        #                  student3 has 1 delivery
        #                  student4 has 0 deliveries
        self.assertEquals(Delivery.published_where_is_candidate(student1).count(), 2)
        self.assertEquals(Delivery.published_where_is_candidate(student2).count(), 1)
        self.assertEquals(Delivery.published_where_is_candidate(student3).count(), 1)
        self.assertEquals(Delivery.published_where_is_candidate(student4).count(), 0)
