from django.test import TestCase
from dingus import Dingus

from devilry.apps.restadmin.restnode import RestNode
from devilry.rest.indata import InvalidIndataError

class TestRestNode(TestCase):
    def setUp(self):
        self.nodedao = Dingus()
        self.restnode = RestNode('api', '1.0', self.nodedao)

    def test_crud_read(self):
        result = self.restnode.read(id=10)
        self.assertRaises(InvalidIndataError, self.restnode.read, id="invalid")
        self.assertEquals(1, len(self.nodedao.calls("read", id=10)))
        result_keys = result.keys()
        self.assertEquals(set(result_keys), set(['long_name', 'etag', 'id', 'short_name']))

    def test_crud_list(self):
        result = self.restnode.crud_list(5)
        self.assertEqual(1, len(self.nodedao.calls("list", 5)))
        result_keys = result['items'][0].keys()
        self.assertEqual(set(result_keys), set(RestNode.read_fields))
