"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from models import Node, NodeAdministator


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)



class TestNode(TestCase):
    fixtures = ['testusers.json', 'testdata.json']
    def test_get_path(self):
        print Node.get_pathlist_kw(['uio', 'matnat', 'ifi'])
        print Node.get_by_pathlist(['uio', 'ifi'])


class TestSignals(TestCase):
    def test_node_post_save_handler(self):
        bart = User.objects.create_user('bart', 'bart@example.com', 'bartman')
        ifi = Node(short_name="ifi", long_name="IFI")
        ifi.save()
        n = NodeAdministator(user=bart, node=ifi)
        self.assertRaises(Permission.DoesNotExist, Permission.objects.get,
                content_type__name = 'node',
                codename = 'change_node',
                user=bart)
        n.save()
        permission = Permission.objects.get(
                content_type__name = 'node',
                codename = 'change_node',
                user=bart)




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

