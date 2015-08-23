#!/usr/bin/env python
"""
Tests the StreamableZip and StreamableTar implementations.
"""

# from django.test import TestCase
#
# from devilry.apps.core.models import (Node, Subject, Period, Assignment, AssignmentGroup,
#                                       Delivery, Candidate)

#class TestDeliveryCollection(TestCase):
    #fixtures = ['core/deprecated_users.json', 'core/core.json']

    #def setUp(self):
        #self.thesuperuser= User.objects.get(username='thesuperuser')
        #self.ifi = Node.objects.get(short_name='ifi')
        #self.ifiadmin = User.objects.get(username='ifiadmin') # admin on the ifi node
        #self.inf1100 = Subject.get_by_path('inf1100')
        
        #self.inf1100_long = Period.get_by_path('inf1100.looong')
        #self.assignment = Assignment.get_by_path("inf1100.looong.oblig1")

        #self.userobj = User.objects.get(username="student0")
        #self.ag = AssignmentGroup()
        #self.ag.parentnode = self.assignment
        #cand = Candidate()
        #cand.student = self.userobj
        #cand.assignment_group = self.ag
        #cand.save()
        #self.ag.candidates.add(cand)
        #self.ag.save()
        #

    #def test_something(self):
        #pass
        #delivery = Delivery.begin(self.ag, self.userobj)
        #delivery.add_file("Testfile", f.chunks())
        #delivery.finish()

