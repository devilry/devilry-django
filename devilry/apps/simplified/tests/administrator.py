from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ...core import models
from ..administrator import Node, Subject
from ..exceptions import PermissionDenied


class TestAdministratorNode(TestCase):
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
        node = Node.read_model(self.clarabelle, id=self.univ.id)
        node = Node.read_model(self.grandma, self.univ.id) # superuser allowed
        with self.assertRaises(PermissionDenied):
            node = Node.read_model(self.daisy, self.univ.id) # superuser allowed
        node = Node.read_model(self.grandma, dict(short_name=self.univ.short_name))
        self.assertEquals(node.short_name, 'univ')


    def test_update(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)

        kw = dict(id=self.duckburgh.id,
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
                    id=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.invalidid)
        with self.assertRaises(models.Node.DoesNotExist):
            Node.update(self.clarabelle,
                    id=self.invalidid,
                    short_name='test2',
                    long_name='Test 2',
                    parentnode_id=None)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.update(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)


    def test_delete_asnodeadmin(self):
        Node.delete(self.clarabelle, id=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)

    def test_delete_asnodeadmin_by_short_name(self):
        Node.delete(self.clarabelle, dict(short_name='univ'))
        with self.assertRaises(models.Node.DoesNotExist):
            Node.delete(self.clarabelle, dict(short_name='univ'))

    def test_delete_assuperadmin(self):
        Node.delete(self.grandma, id=self.univ.id)
        with self.assertRaises(models.Node.DoesNotExist):
            node = models.Node.objects.get(id=self.univ.id)
    def test_delete_noperm(self):
        with self.assertRaises(PermissionDenied):
            Node.delete(self.daisy, id=self.univ.id)


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


class TestAdministratorSubject(TestCase):
    fixtures = ["simplified/data.json"]
    
    def setUp(self):
        self.grandma = User.objects.get(username='grandma') # superuser
        self.univ = models.Node.objects.get(short_name='univ')
        self.duck1100 = models.Subject.objects.get(short_name='duck1100')


    def test_read_model(self):
        subject = Subject.read_model(self.grandma, id=self.duck1100.id)
        self.assertEquals(subject.short_name, 'duck1100')
