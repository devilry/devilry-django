from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ...core import models
from ..administrator import Node
from ..exceptions import PermissionDeniedException


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
                models.Node.where_is_admin(self.daisy).count())


    def test_query(self):
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
        qryset = Node.search(self.clarabelle, query="").qryset
        self.assertEquals(len(qryset), 2)

    def test_query_security(self):
        self.duckburgh.admins.add(self.daisy)
        self.assertEquals(1,
                models.Node.where_is_admin(self.daisy).count())

    def test_create(self):
        kw = dict(long_name='Test',
                parentnode_id=self.univ.id)
        node = Node.create(self.clarabelle, short_name='test1', **kw)
        self.assertEquals(node.short_name, 'test1')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

        node = Node.create(self.grandma, short_name='test2', **kw) # superuser allowed
        with self.assertRaises(PermissionDeniedException):
            node = Node.create(self.daisy, short_name='test3', **kw)


    def test_replace(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)

        kw = dict(id=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=self.univ.id)
        node = Node.replace(self.clarabelle, **kw)
        self.assertEquals(node.short_name, 'test')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)

        node = Node.replace(self.grandma, **kw) # superuser allowed
        with self.assertRaises(PermissionDeniedException):
            node = Node.replace(self.daisy, **kw)

    def test_replace_errors(self):
        invalidid = 100000
        self.assertRaises(models.Node.DoesNotExist, models.Node.objects.get,
                id=invalidid)
        self.assertRaises(models.Node.DoesNotExist,
                Node.replace,
                    self.clarabelle,
                    id=self.duckburgh.id,
                    short_name='test',
                    long_name='Test',
                    parentnode_id=invalidid)
        with self.assertRaisesRegexp(ValidationError,
                "long_name.*short_name"):
            Node.replace(
                    self.clarabelle, self.duckburgh.id,
                    short_name=None, long_name=None)
