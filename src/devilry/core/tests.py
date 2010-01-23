"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from models import Node


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)


class TestSignals(TestCase):
    def test_add_permissions_to_users(self):
        bart = User.objects.create_user('bart', 'bart@example.com', 'bartman')
        ifi = Node(name="ifi", displayname="IFI")
        ifi.save()
        ifi.admins.add(bart)
        
        


#class BasicNodeHierarchy:
    #def setUp(self):
        #self.uio = models.Node(name="uio", displayname="UiO")
        #self.ifi = models.Node(name="ifi", displayname="IFI")
        ##self.infx = models.

#class TestDelivery(TestCase):
    #def test_unicode(self):


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

