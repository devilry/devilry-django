"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from models import Node, NodeAdministator


class TestNode(TestCase):
    fixtures = ['testusers.json', 'testdata.json']
    def test_get_pathlist_kw(self):
        self.assertEquals(Node.get_pathlist_kw(['uio', 'matnat', 'ifi']),
                {'parent__short_name': 'matnat', 'parent__parent__short_name': 'uio', 'short_name': 'ifi'})

    def test_get_by_pathlist(self):
        self.assertEquals(Node.get_by_pathlist(['uio', 'matnat', 'ifi']).short_name, 'ifi')
        self.assertRaises(Node.DoesNotExist, Node.get_by_pathlist, ['uio', 'ifi'])

    def test_get_by_path(self):
        self.assertEquals(Node.get_by_path('uio.matnat.ifi').short_name, 'ifi')
        self.assertRaises(Node.DoesNotExist, Node.get_by_path, 'uio.ifi')

    def test_create_by_pathlist(self):
        n = Node.create_by_pathlist(['this', 'is', 'a', 'test'])
        self.assertEquals(n.short_name, 'test')
        Node.get_by_path('this.is.a.test') # Tests if it has been saved


class TestSignals(TestCase):
    def test_node_post_save_handler(self):
        #bart = User.objects.create_user('bart', 'bart@example.com', 'bartman')
        #ifi = Node(short_name="ifi", long_name="IFI")
        #ifi.save()
        #n = NodeAdministator(user=bart, node=ifi)
        #self.assertRaises(Permission.DoesNotExist, Permission.objects.get,
                #content_type__name = 'node',
                #codename = 'change_node',
                #user=bart)
        #n.save()
        #permission = Permission.objects.get(
                #content_type__name = 'node',
                #codename = 'change_node',
                #user=bart)

        fry = Users.objects.get(username='')
        permission = Permission.objects.get(
                content_type__name = 'node',
                codename = 'change_node',
                user=bart)
