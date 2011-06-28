from django.test import TestCase
from django.contrib.auth.models import User

from ....simplified import PermissionDenied
from ...core import models
from ...core import pluginloader
from ..simplified import Delivery

import datetime


class SimplifiedDeliveryTestCase(TestCase):

    fixtures = ["simplified/data.json"]

    # def setUp(self):
    #      self.duck1100_core = models.Subject.objects.get(short_name='duck1100')
    #      self.duck1080_core = models.Subject.objects.get(short_name='duck1080')
    #      self.duck3580_core = models.Subject.objects.get(short_name='duck3580')
    #
    #      self.duck1100user = User.objects.create(username='duck1100student')
    #      ag = self.duck1100_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0]
    #      self.duck1100candidate = models.Candidate.objects.create(student=self.duck1100user, assignment_group=ag)
    #
    #      self.duck1100_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].candidates.add(self.duck1100candidate)
    #
    #      self.duck1080user = User.objects.create(username='duck1080student')
    #      self.duck1080candidate = models.Candidate.objects.create(student=self.duck1080user)
    #      self.duck1080_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].candidate.add(self.duck1080candidate)
    #
    #      self.duck3580user = User.objects.create(username='duck3580student')
    #      self.duck3580candidate = models.Candidate.objects.create(student=self.duck3580user)
    #      self.duck3580_core.periods.all()[0].assignments.all()[0].assignmentgroups.all()[0].candidate.add(self.duck1080candidate)


class TestSimplifiedDelivery(SimplifiedDeliveryTestCase):

    def test_search(self):

        candidate0 = User.objects.get(username="student0")

        # student0 has 11 deliveries total
        #               4 deliveries in duck1100
        #               4 deliveries in duck3580

        # check that:
        #   all deliveries are returned
        self.assertEquals(Delivery.search(candidate0).qryset.count(), 9)

        #   that a bogus search returns 0 hits
        self.assertEquals(Delivery.search(candidate0, query="this_hopefully_does_not_return_anything").qryset.count(), 0)

        #   all deliveries in subject duck1100 are returned
        self.assertEquals(Delivery.search(candidate0, query="duck1100").qryset.count(), 4)

        #   all deliveries in subject duck3580 are returned
        self.assertEquals(Delivery.search(candidate0, query="duck3580").qryset.count(), 2)

        #   all deliveries from period "h01" are returned
        self.assertEquals(Delivery.search(candidate0, query="fall01").qryset.count(), 5)

        #   all deliveries from assignment "week1" are returned
        self.assertEquals(Delivery.search(candidate0, query="week1").qryset.count(), 3)

    def test_read(self):

        candidate0 = User.objects.get(username="student0")

        #        deliveries = models.Delivery.objects.filter(assignment_group__candidates__student=candidate0).all()
        delivery = Delivery.read(candidate0, Delivery.search(candidate0).qryset[0].id, ["subject","period","subject"])
        self.assertEquals(delivery['number'], 1)
        self.assertEquals(delivery['successful'], 1)
        # TODO: test time_of_delivery in some way
        self.assertEquals(delivery['time_of_delivery'], datetime.datetime.now())
