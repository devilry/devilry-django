"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.core.exceptions import ValidationError
from models import Node, Subject, Period, Assignment, AssignmentGroup, Delivery



class TestNode(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def setUp(self):
        self.ifi = Node.objects.get(pk=1)
        self.uio = Node.objects.get(pk=2)

    def test_get_pathlist_kw(self):
        self.assertEquals(Node._get_pathlist_kw(['uio', 'matnat', 'ifi']), {
                'short_name': 'ifi',
                'parentnode__short_name': 'matnat',
                'parentnode__parentnode__short_name': 'uio'})

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

    def test_get_nodepks_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        pks = Node._get_nodepks_where_isadmin(uioadmin)
        pks.sort()
        self.assertEquals(pks, [1,2,3])

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Node.where_is_admin(uioadmin).count(), 3)

    def test_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        ifiadmin = User.objects.get(username='ifiadmin')
        teacher1 = User.objects.get(username='teacher1')
        self.assertTrue(self.ifi.is_admin(uioadmin))
        self.assertTrue(self.ifi.is_admin(ifiadmin))
        self.assertFalse(self.ifi.is_admin(teacher1))

    def test_iter_childnodes(self):
        c = [node for node in self.uio.iter_childnodes()]
        self.assertEquals(len(c), 2)

    def test_clean_parent_is_child(self):
        """ Can not be child of it's own child. """
        self.uio.parentnode = self.ifi
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_parent_is_self(self):
        """ Can not be child of itself. """
        self.uio.parentnode = self.uio
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_parent_none(self):
        """ Only one node can be root. """
        self.ifi.parentnode = None
        self.assertRaises(ValidationError, self.ifi.clean)


class TestNodeNoFixture(TestCase):
    def test_clean_noroot(self):
        """ At least one node *must* be root. """
        uio = Node()
        uio.short_name = 'uio'
        uio.long_name = 'uio'
        uio.parent = None
        self.assertRaises(ValidationError, uio.clean)


class TestSubject(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Subject.where_is_admin(uioadmin).count(), 2)


class TestPeriod(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Period.where_is_admin(uioadmin).count(), 5)


class TestAssignment(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Assignment.where_is_admin(uioadmin).count(), 2)


class TestAssignmentGroup(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(AssignmentGroup.where_is_admin(uioadmin).count(), 2)

    def test_where_is_student(self):
        student2 = User.objects.get(username='student2')
        self.assertEquals(AssignmentGroup.where_is_student(student2).count(), 2)

    def test_where_is_examiner(self):
        teacher2 = User.objects.get(username='teacher2')
        self.assertEquals(AssignmentGroup.where_is_examiner(teacher2).count(), 2)


class TestDelivery(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Delivery.where_is_admin(uioadmin).count(), 3)

    def test_where_is_student(self):
        student2 = User.objects.get(username='student2')
        self.assertEquals(Delivery.where_is_student(student2).count(), 3)

    def test_where_is_examiner(self):
        teacher2 = User.objects.get(username='teacher2')
        self.assertEquals(Delivery.where_is_examiner(teacher2).count(), 3)

