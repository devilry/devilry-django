from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestRecentFeedbacks(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')
        self.group = self.testhelper.sub_p1_a1_g1
        self.url = '/devilry_student/rest/recent-feedbacks/'

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

    def test_recent_feedbacks_minimal(self):
        fileinfo = {'ok.py': ['print ', 'meh']}
        delivery = self.testhelper.add_delivery('sub.p1.a1.g1', fileinfo)
        self.testhelper.add_feedback(delivery,
                                     verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})

        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'assignment', 'period', 'subject',
                               'number', 'last_feedback', 'group']))

    def test_recent_deliveries_overflow(self):
        fileinfo = {'ok.py': ['print ', 'meh']}
        for x in xrange(8):
            delivery = self.testhelper.add_delivery('sub.p1.a1.g1', fileinfo)
            self.testhelper.add_feedback(delivery,
                                         verdict={'grade': '{0}/100'.format(x), 'points': x, 'is_passing_grade': False})
        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 6)

