from django.test import TestCase
import views


import cStringIO
from xmlrpclib import Transport
from django.test.client import Client
from xmlrpclib import ServerProxy
from xmlrpclib import getparser, ProtocolError
import xmlrpclib


class DjangoTestClientTransport(object):

    def __init__(self):
        self.client = Client()

    def getparser(self):
        return getparser()

    def request(self, host, handler, request_body, verbose = False):
        parser, unmarshaller = self.getparser()
        response = self.client.post(handler, request_body, 'text/xml')
        if response.status_code != 200:
            raise ProtocolError(
              '%s%s' % (host, handler),
              response.status_code,
              httplib.responses.get(response.status_code, ''),
              dict(response.items()),
            )
        parser.feed(response.content)
        return unmarshaller.close()

def get_serverproxy():
    return ServerProxy('http://localhost/xmlrpc/',
            transport=DjangoTestClientTransport())


class TestXmlRpc(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json']
    def setUp(self):
        self.s = get_serverproxy()

    def assertLoginRequired(self, method, *args, **kwargs):
        self.assertRaises(xmlrpclib.Fault, method, *args, **kwargs)

    def test_login(self):
        self.assertLoginRequired(self.s.sum, 1, 2)
        self.assertEquals(self.s.login('thesuperuser', 'test'),
                views.SUCCESSFUL_LOGIN)
        self.s.login('thesuperuser', 'test')
        self.assertEquals(self.s.sum(1, 2), "Hello thesuperuser. 1+2 == 3")
