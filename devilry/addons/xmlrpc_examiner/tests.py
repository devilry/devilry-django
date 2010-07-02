from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from devilry.core.models import Assignment, Delivery, FileMeta
from devilry.core.deliverystore import MemoryDeliveryStore


class TestXmlRpc(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

    def setUp(self):
        self.client = Client()
        self.s = get_serverproxy(self.client, '/xmlrpc_examiner/')

    def test_list_active_assignments(self):
        self.assertLoginRequired(self.s.list_active_assignments)
        self.login(self.client, 'examiner4')
        lst = self.s.list_active_assignments()
        self.assertEquals(len(lst), 1)
        o1 = lst[0]
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(o1['id'], 1)
        self.assertEquals(o1['short_name'], oblig1.short_name)
        self.assertEquals(o1['long_name'], oblig1.long_name)
        self.assertEquals(o1['path'], oblig1.get_path())
        self.assertEquals(o1['publishing_time'], oblig1.publishing_time)
        self.assertEquals(o1['deadline'], oblig1.deadline)

        future = datetime.now() + timedelta(10)
        oldone = Assignment.objects.get(id=3)
        oldone.parentnode.end_time = future
        oldone.parentnode.save()
        lst = self.s.list_active_assignments()
        self.assertEquals(len(lst), 2)

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

    def test_list_deliveries(self):
        FileMeta.deliverystore = MemoryDeliveryStore()
        self.assertLoginRequired(self.s.list_deliveries, 1)
        self.login(self.client, 'examiner1')
        d = Delivery.objects.get(pk=3)
        d.add_file('test.txt', ['test'])
        d.add_file('test2.txt', ['test2'])
        d.finish()
        lst = self.s.list_deliveries(1)
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['id'], 3)
        self.assertTrue(
                lst[0]['time_of_delivery']
                > lst[1]['time_of_delivery'])
        filemetas = lst[0]['filemetas']
        self.assertEquals(len(filemetas), 2)
        self.assertEquals(['test.txt', 'test2.txt'],
                [f['filename'] for f in filemetas])
