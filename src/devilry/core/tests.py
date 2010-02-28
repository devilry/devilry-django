"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from models import Node, Subject, Period, Assignment, DeliveryGroup, DeliveryCandidate


class TestNode(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def setUp(self):
        self.ifi = Node.objects.get(pk=1)
        self.uio = Node.objects.get(pk=2)

    def test_get_pathlist_kw(self):
        self.assertEquals(Node.get_pathlist_kw(['uio', 'matnat', 'ifi']), {
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
        pks = Node.get_nodepks_where_isadmin(uioadmin)
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


class TestDelivery(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(DeliveryGroup.where_is_admin(uioadmin).count(), 2)

    def test_where_is_student(self):
        student2 = User.objects.get(username='student2')
        self.assertEquals(DeliveryGroup.where_is_student(student2).count(), 2)

    def test_where_is_examiner(self):
        teacher2 = User.objects.get(username='teacher2')
        self.assertEquals(DeliveryGroup.where_is_examiner(teacher2).count(), 2)


class TestDeliveryCandidate(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(DeliveryCandidate.where_is_admin(uioadmin).count(), 3)

    def test_where_is_student(self):
        student2 = User.objects.get(username='student2')
        self.assertEquals(DeliveryCandidate.where_is_student(student2).count(), 3)

    def test_where_is_examiner(self):
        teacher2 = User.objects.get(username='teacher2')
        self.assertEquals(DeliveryCandidate.where_is_examiner(teacher2).count(), 3)



class TestFileMeta(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_qry_where_is_admin(self):
        """ TODO """

    def test_qry_where_is_student(self):
        """ TODO """

    def test_qry_where_is_examiner(self):
        """ TODO """
