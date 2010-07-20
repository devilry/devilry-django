import cStringIO
from xmlrpclib import Transport
from xmlrpclib import ServerProxy, Fault
from xmlrpclib import getparser, ProtocolError
import httplib


class XmlrpcTestClientTransport(object):

    def __init__(self, client, use_datetime=True):
        self.client = client
        self.use_datetime = use_datetime

    def getparser(self):
        return getparser(use_datetime=self.use_datetime)

    def request(self, host, handler, request_body, verbose=False):
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


def get_serverproxy(client, path):
    return ServerProxy('http://localhost' + path,
            transport=XmlrpcTestClientTransport(client))

class XmlRpcAssertsMixin(object):
    def assertLoginRequired(self, method, *args, **kwargs):
        self.assertRaises(Fault, method, *args, **kwargs)

    def login(self, client, username):
        get_serverproxy(client, '/xmlrpc/').login(username, 'test')

    def logout(self, client):
        get_serverproxy(client, '/xmlrpc/').logout()
