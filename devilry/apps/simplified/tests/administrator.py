from django.test import TestCase
from django.contrib.auth.models import User

from ...core import models
from ..administrator import Node


class TestAdministratorNode(TestCase):
    fixtures = ["simplified/data.json"]

    def test_get(self):
        grandma = User.objects.get(username="grandma")
        nodes = models.Node.objects.all().order_by("short_name")
        qryset = Node.getqry(grandma).qryset
        self.assertEquals(len(qryset), len(nodes))
        self.assertEquals(qryset[0].short_name, nodes[0].short_name)

        # query
        qryset = Node.getqry(grandma, query="burgh").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.getqry(grandma, query="univ").qryset
        self.assertEquals(len(qryset), 1)
        qryset = Node.getqry(grandma, query="").qryset
        self.assertEquals(len(qryset), 2)

    def test_get_security(self):
        daisy = User.objects.get(username="daisy")
        self.assertEquals(0,
                models.Node.objects.filter(admins__username='daisy').count())
        node = models.Node.objects.get(short_name='duckburgh')
        node.admins.add(daisy)
        self.assertEquals(1,
                models.Node.objects.filter(admins__username='daisy').count())

