from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json

from ..restful import RestNode
from ...core import models



class TestAdministratorRestNodeNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestNode._searchform_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"], query=''))
        #print RestNode.extjs_model


class TestAdministratorRestNode(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.client = Client()
        self.client.login(username="clarabelle", password="test")
        clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.univ.admins.add(clarabelle)

    def test_search(self):
        url = RestNode.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True},
                content_type='application/json')
        data = json.loads(r.content)['items']
        first = data[0]
        self.assertEquals(first, {
            u'id': 2,
            u'short_name': u'univ',
            u'long_name': u'Univ',
            u'parentnode__id': None
            })

    def test_create(self):
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 0)
        url = RestNode.get_rest_url(self.univ.id)
        data = dict(short_name='testnode', long_name='Test Node', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertTrue(response['success'])
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 1)
        fromdb = models.Node.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'testnode')
        self.assertEquals(fromdb.long_name, 'Test Node')
        self.assertEquals(fromdb.parentnode, None)

    def test_create_errors(self):
        url = RestNode.get_rest_url(self.univ.id)
        data = dict(short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            success = False,
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            non_field_errors = []))

    def test_update(self):
        url = RestNode.get_rest_url(self.univ.id)
        data = dict(id=2, short_name='univ', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(success=True, id=2))

    def test_update_errors(self):
        url = RestNode.get_rest_url(self.univ.id)
        data = dict(id=2, short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            success = False,
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            non_field_errors = []))


    def test_delete(self):
        url = RestNode.get_rest_url(self.univ.id)

        # TODO: delete should not be recursive
        self.assertEquals(models.Node.objects.filter(id=self.univ.id).count(), 1)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(models.Node.objects.filter(id=self.univ.id).count(), 0)
