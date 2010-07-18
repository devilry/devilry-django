from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from devilry.core.models import Assignment, Delivery, FileMeta, Feedback
from devilry.core.deliverystore import MemoryDeliveryStore


class TestXmlRpc(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

class HelloTest(TestCase):
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEquals((1 + 2), 3)
        self.assertEquals(0 + 1, 1)
    def testMultiply(self):
        self.assertEquals((0 * 10), 0)
        self.assertEquals((5 * 8), 40)

#if __name__ == '__main__':
    #unittest.main()
