from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from ..examiner import RestSubjects, RestPeriods, RestAssignments



class TestRestSubjectsNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestSubjects._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["long_name"], query='', format='json'))

class TestRestSubjects(TestCase):
    fixtures = ["tests/simplified/data.json"]
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
            u'path': u'duck1080'})


class TestRestPeriodsNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestPeriods._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["long_name"], query='',
                format='json', subject_short_name=''))

class TestRestPeriods(TestCase):
    fixtures = ["tests/simplified/data.json"]
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
            u'path': u'duck1100/h01'})



class TestRestAssignmentsNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestAssignments._getdata_to_kwargs({})
        self.assertEquals(kw, dict(
                limit=50, start=0, orderby=["short_name"],
                old=True, active=True, query=u'', longnamefields=False,
                pointhandlingfields=False, format='json'
            ))

class TestRestAssignments(TestCase):
    fixtures = ["tests/simplified/data.json"]
    url = reverse('devilry-restful-examiner-assignments')

    def setUp(self):
        self.client = Client()
        self.client.login(username="examiner1", password="test")

    def test_get(self):
        r = self.client.get(self.url, data=dict(format='json'))
        data = json.loads(r.content)
        first = data['items'][0]
        keys = first.keys()
        keys.sort()
        self.assertEquals(keys,
                ['id', 'long_name',
                'parentnode__parentnode__short_name',
                'parentnode__short_name',
                'path', 'short_name'])

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
