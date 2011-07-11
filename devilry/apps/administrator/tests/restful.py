from django.test import TestCase
from django.test.client import Client
import json

from ..restful import (RestfulSimplifiedNode, RestfulSimplifiedAssignment)
from ..simplified import SimplifiedAssignment
from ...core import models, testhelper



class TestAdministratorRestfulSimplifiedNode(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni:admin(admin1)')
        self.client = Client()
        self.client.login(username="admin1", password="test")

    def test_search(self):
        url = RestfulSimplifiedNode.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(first, {'id': self.uni.id,
                                  'short_name': self.uni.short_name,
                                  'long_name': self.uni.long_name,
                                  'parentnode': None
                                 })

    def test_create(self):
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 0)
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='testnode', long_name='Test SimplifiedNode', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 200)
        response = json.loads(r.content)
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 1)
        fromdb = models.Node.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'testnode')
        self.assertEquals(fromdb.long_name, 'Test SimplifiedNode')
        self.assertEquals(fromdb.parentnode, None)

    def test_create_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 400)
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))

    def test_update(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='univ', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, {'id': self.uni.id,
                                     'short_name': 'univ',
                                     'long_name': 'Univ',
                                     'parentnode': None})

    def test_update_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))

    def test_delete(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 1)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 0)



class TestAdministratorRestfulSimplifiedAssignment(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem:admin(admin2)'],
                 assignments=['a1', 'a2'])
        self.client = Client()
        self.client.login(username="admin1", password="test")

    def test_search_fieldgroups(self):
        resultfields = SimplifiedAssignment._meta.resultfields
        url = RestfulSimplifiedAssignment.get_rest_url()

        r = self.client.get(url, data={'getdata_in_qrystring': True})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(set(first.keys()), set(resultfields.aslist()))

        r = self.client.get(url, data={'getdata_in_qrystring': True,
                                       'result_fieldgroups': json.dumps(['subject', 'period', 'pointfields'])})
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data['items'][0]
        all_resultfields = resultfields.aslist(resultfields.additional_aslist())
        self.assertEquals(set(first.keys()), set(all_resultfields))
