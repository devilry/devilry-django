from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from devilry.core.models import Assignment


class TestXmlRpc(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

    def setUp(self):
        self.client = Client()
        self.s = get_serverproxy(self.client, '/xmlrpc_examiner/')

    def test_list_assignmentgroups(self):
        self.assertLoginRequired(self.s.list_assignmentgroups, 1)
        self.login(self.client, 'examiner1')
        lst = self.s.list_assignmentgroups(1)
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['id'], 1)
        self.assertEquals(lst[1]['id'], 2)
        self.assertEquals(lst[1]['students'], ['student2', 'student3'])
        self.assertEquals(lst[0]['number_of_deliveries'], 2)

        a = Assignment.objects.get(id=1)
        a.anonymous = True
        a.save()
        lst = self.s.list_assignmentgroups(1)
        self.assertEquals(lst[1]['students'], ['2', '3'])
