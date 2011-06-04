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
                limit=50, start=0, orderby=["short_name"], query='', format='json'))


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
        r = self.client.get(url, data={'format':'json', 'id':1})
        data = json.loads(r.content)['items']
        first = data[0]
        self.assertEquals(first, {u'long_name': u'Univ', u'id': 2, u'short_name': u'univ'})

    def test_put(self):
        url = reverse('devilry-restful-administrator-node', args=[self.univ.id])
        r = self.client.put(url, data=dict(short_name='test'))
        print r.content
        #data = json.loads(r.content)['items']
