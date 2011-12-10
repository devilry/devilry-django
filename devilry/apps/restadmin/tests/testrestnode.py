from django.test import TestCase
from dingus import Dingus, DontCare

from devilry.apps.restadmin.restnode import RestNode
from devilry.rest.indata import InvalidIndataError

def dummy_urlreverse(restcls, apipath, apiversion, id=None):
    return '{0}-{1}.{2}-{3}'.format(restcls.__name__, apipath, apiversion, id)


class TestRestNode(TestCase):
    def setUp(self):
        self.restnode = RestNode(nodedaocls=Dingus, apipath='api', apiversion='1.0', user=None, url_reverse=dummy_urlreverse)
        self.nodedao = self.restnode.nodedao

    def test_read(self):
        result = self.restnode.read(id=10)
        self.assertRaises(InvalidIndataError, self.restnode.read, id="invalid")
        self.assertEquals(1, len(self.nodedao.calls("read", self.restnode.user, 10)))
        self.assertEqual(set(result.keys()), set(['item', 'links']))

    def test_list(self):
        result = self.restnode.list(parentnode_id=5)
        self.assertEqual(1, len(self.nodedao.calls("list", self.restnode.user, 5)))
        self.assertEqual(set(result.keys()), set(['items', 'links', 'total', 'params']))
        self.assertEqual(result['params']['parentnode_id'], 5)
        self.assertEqual(set(result['items'][0].keys()), set(['item', 'links']))


    def test_create(self):
        result = self.restnode.create(short_name='hello', long_name='Hello World')
        self.assertEqual(1, len(self.nodedao.calls("create")))
        self.assertEqual(set(result.keys()), set(['item', 'links']))