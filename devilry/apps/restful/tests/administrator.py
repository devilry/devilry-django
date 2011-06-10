from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from ..administrator import RestNode
from ...core import models



class TestAdministratorRestNodeNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestNode._searchform_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"], query=''))
        print RestNode.extjs_model


class TestAdministratorRestNode(TestCase):
    fixtures = ["simplified/data.json"]

    def setUp(self):
        self.client = Client()
        self.client.login(username="clarabelle", password="test")
        clarabelle = User.objects.get(username="clarabelle")
        self.univ = models.Node.objects.get(short_name='univ')
        self.univ.admins.add(clarabelle)

    def test_get(self):
        url = reverse('devilry-restful-administrator-nodesearch')
        r = self.client.get(url, data={'id':1},
                content_type='application/json')
        data = json.loads(r.content)['items']
        first = data[0]
        self.assertEquals(first, {
            u'id': 2,
            u'short_name': u'univ',
            u'long_name': u'Univ',
            u'parentnode__id': None
            })

    def test_post(self):
        url = reverse('devilry-restful-administrator-node', args=[self.univ.id])
        data = dict(short_name='testnode', long_name='Test Node', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertTrue(response['success'])
        fromdb = models.Node.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'testnode')
        self.assertEquals(fromdb.long_name, 'Test Node')
        self.assertEquals(fromdb.parentnode, None)

    def test_post_errors(self):
        url = reverse('devilry-restful-administrator-node', args=[self.univ.id])
        data = dict(short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            success = False,
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            non_field_errors = []))

    def test_put(self):
        url = reverse('devilry-restful-administrator-node', args=[self.univ.id])
        data = dict(id=2, short_name='univ', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(success=True, id=2))

    def test_put_errors(self):
        url = reverse('devilry-restful-administrator-node', args=[self.univ.id])
        data = dict(id=2, short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            success = False,
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            non_field_errors = []))
