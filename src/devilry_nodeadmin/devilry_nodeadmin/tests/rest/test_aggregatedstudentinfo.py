from django.test import TestCase
from django.core.urlresolvers import reverse
import time
from urllib import urlencode

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestAggregatedStudentInfo(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.client = RestClient()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1).d1:ends(5)')
        self.group = self.testhelper.sub_p1_a1_g1


    def _get(self, user_id):
        return self.client.rest_get(reverse('devilry_nodeadmin-aggregatedstudentinfo', kwargs={'user_id': user_id}))

    def _getas(self, username, id):
        self.client.login(username=username, password='test')
        return self._get(id)

    def test_get(self):
        content, response = self._getas('uniadmin', self.testhelper.student1.id)
        self.assertEquals(response.status_code, 200)
        #self.assertEquals(content, ['Hello', 'world'])

    def test_get_noauth(self):
        content, response = self._get(self.testhelper.student1.id)
        self.assertEquals(response.status_code, 401)
