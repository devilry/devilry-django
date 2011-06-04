from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from ..examiner import RestSubject, RestPeriod, RestAssignment



class TestRestSubjectNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestSubject._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"], query='', format='json'))

class TestRestSubject(TestCase):
    fixtures = ["simplified/data.json"]
    url = reverse('devilry-restful-examiner-tree-subjects')

    def setUp(self):
        self.client = Client()
        self.client.login(username="examiner1", password="test")

    def test_get(self):
        r = self.client.get(self.url, data=dict(format='json'))
        data = json.loads(r.content)['items']
        first = data[0]
        self.assertEquals(first, {
            u'long_name': u'DUCK1080 - Making the illogical seem logical',
            u'id': 2,
            u'short_name': u'duck1080',
            u'path': u'/duck1080'})


class TestRestPeriodNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestPeriod._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"], query='',
                format='json', subject_short_name=''))

class TestRestPeriod(TestCase):
    fixtures = ["simplified/data.json"]
    url = reverse('devilry-restful-examiner-tree-periods', args=['duck1100'])

    def setUp(self):
        self.client = Client()
        self.client.login(username="examiner1", password="test")

    def test_get(self):
        r = self.client.get(self.url, data=dict(format='json'))
        data = json.loads(r.content)['items']
        first = data[0]
        self.assertEquals(first, {
            u'parentnode__short_name': u'duck1100',
            u'long_name': u'Spring year zero',
            u'id': 1,
            u'short_name': u'h01',
            u'path': u'/duck1100/h01'})



class TestRestAssignmentNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestAssignment._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"],
                old=True, active=True, query=u'', longnamefields=False,
                pointhandlingfields=False, format='json',
                period_short_name = '', subject_short_name=''
            ))

class TestRestAssignment(TestCase):
    fixtures = ["simplified/data.json"]
    url = reverse('devilry-restful-examiner-assignments')

    def setUp(self):
        self.client = Client()
        self.client.login(username="examiner1", password="test")

    def test_get(self):
        r = self.client.get(self.url, data=dict(format='json'))
        data = json.loads(r.content)
        first = data['items'][0]
        self.assertEquals(first, {
            u'short_name': u'week1',
            u'parentnode__short_name': u'h01',
            u'long_name': u'The one and only week one',
            u'parentnode__parentnode__short_name': u'duck1100',
            u'path': u'/duck1100/h01/week1',
            u'id': 1})

    def test_get_manyargs(self):
        r = self.client.get(self.url, data=dict(format='json',
            count=3, start=2,
            longnamefields=True,
            orderby='-short_name'))
        data = json.loads(r.content)['items']
        self.assertEquals(len(data[0]), 8)
        self.assertEquals(data[0]['short_name'], 'week3')
        self.assertEquals(data[0]['parentnode__parentnode__short_name'],
                'duck1100')
        self.assertEquals(data[1]['parentnode__parentnode__short_name'],
                'duck1080')
