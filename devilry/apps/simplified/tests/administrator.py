from django.test import TestCase
from django.contrib.auth.models import User

from ...core import models
from ..administrator import Node


class TestAdministratorNode(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.clarabelle = User.objects.get(username="clarabelle")
        self.daisy = User.objects.get(username="daisy")
        self.univ = models.Node.objects.get(short_name='univ')
        self.duckburgh = models.Node.objects.get(short_name='duckburgh')
        self.univ.admins.add(self.clarabelle)
        self.duckburgh.admins.add(self.clarabelle)
        

    def test_get(self):
        clarabelle = User.objects.get(username="clarabelle")
        nodes = models.Node.objects.all().order_by("short_name")
        qryset = Node.getqry(self.clarabelle).qryset
        self.assertEquals(len(qryset), len(nodes))
        self.assertEquals(qryset[0].short_name, nodes[0].short_name)

        # query
        qryset = Node.getqry(self.clarabelle, query="burgh").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.getqry(self.clarabelle, query="univ").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.getqry(self.clarabelle, query="").qryset
        self.assertEquals(len(qryset), 2)

    def test_get_security(self):
        self.assertEquals(0,
                models.Node.where_is_admin(self.daisy).count())
        self.duckburgh.admins.add(self.daisy)
        self.assertEquals(1,
                models.Node.where_is_admin(self.daisy).count())

    def test_replaceitem(self):
        self.assertEquals(self.duckburgh.short_name, 'duckburgh')
        self.assertEquals(self.duckburgh.long_name, 'Duckburgh')
        self.assertEquals(self.duckburgh.parentnode, None)
        node = Node.replaceitem(self.clarabelle,
                id=self.duckburgh.id,
                short_name='test',
                long_name='Test',
                parentnode_id=self.univ.id)
        self.assertEquals(node.short_name, 'test')
        self.assertEquals(node.long_name, 'Test')
        self.assertEquals(node.parentnode, self.univ)
