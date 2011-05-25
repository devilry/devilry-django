from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from ..examiner import RestAssignments

class TestRestAssignmentsNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestAssignments._getdata_to_kwargs({'format':'json'})
        self.assertEquals(kw, dict(
                count=50, start=0, orderby=["short_name"],
                old=True, active=True, search=u'', longnamefields=False,
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
        first = data[0]
        self.assertTrue('id' in first)
        self.assertTrue('short_name' in first)
        self.assertTrue('parentnode__short_name' in first)
        self.assertTrue('parentnode__parentnode__short_name' in first)

    def test_get_manyargs(self):
        r = self.client.get(self.url, data=dict(format='json',
            count=3, start=2,
            longnamefields=True,
            orderby='-short_name'))
        data = json.loads(r.content)
        self.assertEquals(len(data[0]), 7)
        self.assertEquals(data[0]['short_name'], 'week3')
        self.assertEquals(data[0]['parentnode__parentnode__short_name'],
                'duck1100')
        self.assertEquals(data[1]['parentnode__parentnode__short_name'],
                'duck1080')
