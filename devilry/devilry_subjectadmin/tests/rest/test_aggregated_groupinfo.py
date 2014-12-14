from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient


class TestRestAggregatedGroupInfo(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1:admin(a1admin)'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1).d1:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d2:ends(10)')
        self.group = self.testhelper.sub_p1_a1_g1
        self.url = '/devilry_subjectadmin/rest/aggregated-groupinfo/{0}'.format(self.group.id)

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody')
        self.assertEquals(response.status_code, 403)

    def test_groupinfo(self):
        content, response = self._getas('a1admin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(set(content.keys()),
                          set(['id', 'deadlines']))
        self.assertEquals(content['id'], self.group.id)

    def test_groupinfo_superuser(self):
        self.testhelper.create_superuser('superuser')
        content, response = self._getas('superuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(set(content.keys()),
                          set(['id', 'deadlines']))
        self.assertEquals(content['id'], self.group.id)

    def test_deadlines(self):
        content, response = self._getas('a1admin')
        deadlines = content['deadlines']
        self.assertEquals(len(deadlines), 2)
        self.assertEquals(set(deadlines[0].keys()),
                          set(['id', 'deadline', 'deliveries', 'text',
                               'offset_from_now', 'in_the_future']))
