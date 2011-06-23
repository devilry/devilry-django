from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ....simplified import PermissionDenied
from ...core import models
from ..simplified import Node, Subject


class TestSimplifiedAdministratorNode(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)

        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())

        self.invalidid = 100000
        self.assertRaises(models.Node.DoesNotExist, models.Node.objects.get,
                id=self.invalidid)



    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        node = Node.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(node.short_name, 'test1')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

        node = Node.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Node.create(self.daisy, short_name='test3', **kw)

    def test_create_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            Node.create(self.clarabelle,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)

    def test_read_model(self):
        node = Node.read_model(self.clarabelle, idorkw=self.univ.id)
        node = Node.read_model(self.grandma, self.univ.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Node.read_model(self.daisy, self.univ.id) # superuser allowed
        node = Node.read_model(self.grandma, dict(short_name=self.univ.short_name))
        self.assertEquals(node.short_name, 'univ')
        node = Node.read_model(self.grandma, idorkw=self.univ.id)
        self.assertEquals(node.short_name, 'univ')


    def test_update(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)

        kw = dict(idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        node = Node.update(self.clarabelle, **kw)
        self.assertEquals(node.short_name, 'test')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

        node = Node.update(self.grandma, **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Node.update(self.daisy, **kw)

        node = Node.update(self.grandma,
                dict(short_name='test'),
                long_name = 'My Duckburgh Test')
        self.assertEquals(node.long_name, 'My Duckburgh Test')


    def test_update_validation(self):
        with self.assertRaises(models.Node.DoesNotExist):
            Node.update(self.clarabelle,
                    idorkw=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaises(models.Node.DoesNotExist):
            Node.update(self.clarabelle,
                    idorkw=self.invalidid,
                    short_name='test2',
                    long_name='Test 2',
                    parentnode_id=None)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)


    def test_delete_asnodeadmin(self):
        Node.delete(self.clarabelle, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Node.delete(self.clarabelle, dict(short_name='univ'))
        with self.assertRaises(models.Node.DoesNotExist):
            Node.delete(self.clarabelle, dict(short_name='univ'))

    def test_delete_assuperadmin(self):
        Node.delete(self.grandma, idorkw=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)
    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Node.delete(self.daisy, idorkw=self.univ.id)


    def test_search(self):
        clarabelle = User.objects.get(username="clarabelle")
        nodes = models.Node.objects.all().order_by("short_name")
        qryset = Node.search(self.clarabelle).qryset
        self.assertEquals(len(qryset), len(nodes))
        self.assertEquals(qryset[0].short_name, nodes[0].short_name)

        # query
        qryset = Node.search(self.clarabelle, query="burgh").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.search(self.clarabelle, query="univ").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.search(self.clarabelle).qryset
        self.assertEquals(len(qryset), 2)
        qryset = Node.search(self.grandma).qryset
        self.assertEquals(len(qryset), len(nodes))

        self.univ.parentnode = self.duckburgh
        self.univ.save()
        qryset = Node.search(self.grandma,
                parentnode_id=self.duckburgh.id).qryset
        self.assertEquals(len(qryset), 1)
        self.assertEquals(qryset[0].short_name, 'univ')

    def test_search_security(self):
        qryset = Node.search(self.daisy).qryset
        self.assertEquals(len(qryset), 0)

        self.duckburgh.admins.add(self.daisy)
        qryset = Node.search(self.daisy).qryset
        self.assertEquals(len(qryset), 1)


class TestSimplifiedAdministratorSubject(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.duck1100 = models.Subject.objects.get(short_name='duck1100')
        self.clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)
        self.daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.where_is_admin_or_superadmin(self.daisy).count())

    def test_read_model(self):
        subject = Subject.read_model(self.clarabelle, idorkw=self.duck1100.id)
        subject = Subject.read_model(self.grandma, self.duck1100.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Subject.read_model(self.daisy, self.duck1100.id) # superuser allowed
        subject = Subject.read_model(self.grandma, idorkw=self.duck1100.id)
        self.assertEquals(subject.short_name, 'duck1100')
        subject = Subject.read_model(self.grandma,
                dict(short_name=self.duck1100.short_name))
        self.assertEquals(subject.short_name, 'duck1100')

        with self.assertRaises(PermissionDenied):
            node = Subject.read_model(self.daisy, self.duck1100.id) # superuser allowed

    def test_read(self):
        subject = Subject.read(self.grandma, self.duck1100.id)
        self.assertEquals(subject, dict(
                short_name = 'duck1100',
                long_name = self.duck1100.long_name,
                id = self.duck1100.id))

    def test_search(self):
        subjects = models.Subject.where_is_admin_or_superadmin(self.grandma).order_by("short_name")
        qryset = Subject.search(self.grandma).qryset
        self.assertEquals(len(qryset), len(subjects))
        self.assertEquals(qryset[0].short_name, subjects[0].short_name)

        # query
        qryset = Subject.search(self.grandma, query="duck1").qryset
        self.assertEquals(len(qryset), 2)
        qryset = Subject.search(self.grandma, query="duck").qryset
        self.assertEquals(len(qryset), len(subjects))
        qryset = Subject.search(self.grandma, query="1100").qryset
        self.assertEquals(len(qryset), 1)

    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        subject = Subject.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(subject.short_name, 'test1')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)

        subject = Subject.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDenied):
            subject = Subject.create(self.daisy, short_name='test3', **kw)

    def test_update(self):
        self.assertEquals(self.duck1100.short_name, 'duck1100')

        kw = dict(id=self.duck1100.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        subject = Subject.update(self.clarabelle, idorkw=self.duck1100.id, **kw)
        self.assertEquals(subject.short_name, 'test')
        self.assertEquals(subject.long_name, 'Test')
        self.assertEquals(subject.parentnode, self.univ)
        
        with self.assertRaises(PermissionDenied):
            subject = Subject.update(self.daisy, idorkw=self.duck1100.id, **kw)
    
    def test_delete_asnodeadmin(self):
        Subject.delete(self.clarabelle, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Subject.delete(self.clarabelle, dict(short_name='duck1100'))
        with self.assertRaises(models.Subject.DoesNotExist):
            Subject.delete(self.clarabelle, dict(short_name='duck1100'))

    def test_delete_assuperadmin(self):
        Subject.delete(self.grandma, idorkw=self.duck1100.id)
        with self.assertRaises(models.Subject.DoesNotExist):
            subject = models.Subject.objects.get(id=self.duck1100.id)

    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Subject.delete(self.daisy, idorkw=self.duck1100.id)
