from django.test import TestCase
from dingus import Dingus

from devilry.apps.restadmin.restnode import RestNode
from devilry.rest.indata import InvalidIndataError

def dummy_urlreverse(restcls, apipath, apiversion, id=None):
    return '{0}-{1}.{2}-{3}'.format(restcls.__name__, apipath, apiversion, id)

class TestRestNode(TestCase):
    def setUp(self):
        self.restnode = RestNode('api', '1.0', Dingus, url_reverse=dummy_urlreverse)
        self.nodedao = self.restnode.nodedao

    def test_read(self):
        result = self.restnode.read(id=10)
        self.assertRaises(InvalidIndataError, self.restnode.read, id="invalid")
        self.assertEquals(1, len(self.nodedao.calls("read", 10)))
        result_keys = result['item'].keys()
        self.assertEquals(set(result_keys), set(RestNode.read_fields))

    def test_list(self):
        result = self.restnode.list(parentnode_id=5)
        self.assertEqual(1, len(self.nodedao.calls("list", 5)))
        self.assertEqual(set(result['items'][0]['item'].keys()), set(RestNode.read_fields))
        self.assertEqual(set(result['items'][0].keys()), set(['item', 'urls']))