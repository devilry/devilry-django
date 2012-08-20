from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestDeadlinesBulkRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)'], # 2 months ago
                            assignments=['a1:admin(adm):pub(0)']) # 0 days after period begins
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/deadlinesbulk/{0}'.format(self.testhelper.sub_p1_a1.id)

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_get_empty(self):
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['deadlines']), 0)

    def test_get_simple(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['deadlines']), 1)
        d1 = content['deadlines'][0]
        self.assertEquals(set(d1.keys()),
                          set(['deadline', 'text', 'groupcount', 'offset_from_now',
                               'in_the_future']))
        self.assertEquals(d1['groupcount'], 3)
        self.assertEquals(d1['in_the_future'], False)
        self.assertEquals(d1['text'], None)

    def test_get_textdifference(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        # Change text on g1_d1, which should make it a separate entry in the list
        self.testhelper.sub_p1_a1_g1_d1.text = 'Test'
        self.testhelper.sub_p1_a1_g1_d1.save()
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['deadlines']), 2)
        g2_g3_d1 = content['deadlines'][0]
        g1_d1 = content['deadlines'][1]
        self.assertEquals(g1_d1['text'], 'Test')
        self.assertEquals(g1_d1['groupcount'], 1)
        self.assertEquals(g2_g3_d1['text'], None)
        self.assertEquals(g2_g3_d1['groupcount'], 2)

    def test_get_multiple_and_order(self):
        for groupnum in xrange(3):
            # deadline 5 days after assignment starts
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d1:ends(5)'.format(groupnum))
        for groupnum in xrange(2):
            # deadline 70 days after assignment starts, which should be in the future
            self.testhelper.add_to_path('uni;sub.p1.a1.g{0}.d2:ends(70)'.format(groupnum))
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content['deadlines']), 2)
        d1 = content['deadlines'][1]
        d2 = content['deadlines'][0]
        self.assertEquals(d1['groupcount'], 3)
        self.assertEquals(d1['in_the_future'], False)
        self.assertEquals(d2['groupcount'], 2)
        self.assertEquals(d2['in_the_future'], True)

    def test_get_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._listas('nobody')
        self.assertEquals(response.status_code, 403)
