from django.test import TestCase
from django.test.client import Client

import views
from testhelpers import get_serverproxy, XmlRpcAssertsMixin


class TestXmlRpc(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc/users.json']
    def setUp(self):
        self.s = get_serverproxy(Client(), '/xmlrpc/')

    def test_login(self):
        self.assertLoginRequired(self.s.sum, 1, 2)
        self.assertEquals(self.s.login('thesuperuser', 'test'),
                views.SUCCESSFUL_LOGIN)
        self.s.login('thesuperuser', 'test')
        self.assertEquals(self.s.sum(1, 2), "Hello thesuperuser. 1+2 == 3")
        self.s.logout()
        self.assertLoginRequired(self.s.sum, 1, 2)
