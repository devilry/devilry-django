from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient



class TestRestRecentDeliveries(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.group = self.testhelper.sub_p1_a1_g1
        self.url = '/devilry_student/rest/recent-deliveries/'

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_nobody(self):
        fileinfo = {'ok.py': ['print ', 'meh']}
        self.testhelper.add_delivery('sub.p1.a1.g1', fileinfo)
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])

    def test_recent_deliveries_minimal(self):
        fileinfo = {'ok.py': ['print ', 'meh']}
        self.testhelper.add_delivery('sub.p1.a1.g1', fileinfo)

        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'assignment', 'period', 'subject',
                               'time_of_delivery', 'group', 'number']))
        assignment = self.group.parentnode
        period = self.group.parentnode.parentnode
        subject = self.group.parentnode.parentnode.parentnode
        self.assertEquals(content[0]['assignment'],
                          {u'id': assignment.id, u'long_name': u'A1', u'short_name': u'a1'})
        self.assertEquals(content[0]['period'],
                          {u'id': period.id, u'long_name': u'P1', u'short_name': u'p1'})
        self.assertEquals(content[0]['subject'],
                          {u'id': subject.id, u'long_name': u'Sub', u'short_name': u'sub'})

    def test_recent_deliveries_over10(self):
        fileinfo = {'ok.py': ['print ', 'meh']}
        for x in xrange(8):
            self.testhelper.add_delivery('sub.p1.a1.g1', fileinfo)
        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 6)
