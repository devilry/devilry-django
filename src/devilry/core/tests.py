"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from models import Node, Subject, Period, Assignment, Delivery, DeliveryCandidate


class TestNode(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_pathlist_kw(self):
        self.assertEquals(Node.get_pathlist_kw(['uio', 'matnat', 'ifi']), {
                'short_name': 'ifi',
                'parent__short_name': 'matnat',
                'parent__parent__short_name': 'uio'})

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

    def test_get_qryargs_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = Node.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(Node.objects.filter(*args).count(), 3)


class TestSubject(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = Subject.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(Subject.objects.filter(*args).count(), 2)


class TestPeriod(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = Period.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(Period.objects.filter(*args).count(), 5)


class TestAssignment(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = Assignment.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(Assignment.objects.filter(*args).count(), 2)


class TestDelivery(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = Delivery.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(Delivery.objects.filter(*args).count(), 2)

    def test_get_qrykw_where_isstudent(self):
        student2 = User.objects.get(username='student2')
        args = Delivery.get_qryargs_where_isstudent(student2)
        self.assertEquals(Delivery.objects.filter(*args).count(), 2)

    def test_get_qrykw_where_isexaminer(self):
        teacher1 = User.objects.get(username='teacher1')
        args = Delivery.get_qryargs_where_isexaminer(teacher1)
        self.assertEquals(Delivery.objects.filter(*args).count(), 2)


class TestDeliveryCandidate(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        args = DeliveryCandidate.get_qryargs_where_isadmin(uioadmin)
        self.assertEquals(DeliveryCandidate.objects.filter(*args).count(), 3)

    def test_get_qrykw_where_isstudent(self):
        student2 = User.objects.get(username='student2')
        args = DeliveryCandidate.get_qryargs_where_isstudent(student2)
        self.assertEquals(DeliveryCandidate.objects.filter(*args).count(), 3)

    def test_get_qrykw_where_isexaminer(self):
        teacher1 = User.objects.get(username='teacher1')
        args = DeliveryCandidate.get_qryargs_where_isexaminer(teacher1)
        self.assertEquals(DeliveryCandidate.objects.filter(*args).count(), 3)



class TestFileMeta(TestCase):
    fixtures = ['testusers.json', 'testdata.json']

    def test_get_qrykw_where_isadmin(self):
        """ TODO """

    def test_get_qrykw_where_isstudent(self):
        """ TODO """

    def test_get_qrykw_where_isexaminer(self):
        """ TODO """
