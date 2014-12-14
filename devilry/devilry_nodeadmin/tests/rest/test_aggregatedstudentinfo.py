from django.test import TestCase
from django.core.urlresolvers import reverse
import time
from urllib import urlencode

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient


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

        user = {u'username': u'student1', 
                u'displayname': u'student1', 
                u'id': 2, u'full_name': None, 
                u'email': u'student1@example.com'} 
        self.assertEquals(content['user'], user)

        grouped_by_hierarky = content['grouped_by_hierarky'][0]
        self.assertEquals(set(grouped_by_hierarky.keys()), set([u'long_name', u'id', u'short_name', u'periods']))

        period = grouped_by_hierarky['periods'][0]
        self.assertEquals(set(period.keys()), set([u'short_name', u'assignments', 
                                          u'is_relatedstudent', u'start_time', 
                                          u'is_active', u'qualified_forexams', 
                                          u'long_name', u'end_time', u'id']))



        assignments = period['assignments'][0]
        self.assertEquals(set(period.keys()), set([u'short_name', u'assignments', 
                                                   u'is_relatedstudent', u'start_time', 
                                                   u'is_active', u'qualified_forexams', 
                                                   u'long_name', u'end_time', u'id']))

        groups = assignments['groups'][0]
        self.assertEquals(set(groups.keys()), set([u'status', u'active_feedback', u'id']))

    def test_get_noauth(self):
        content, response = self._get(self.testhelper.student1.id)
        self.assertEquals(response.status_code, 401)
