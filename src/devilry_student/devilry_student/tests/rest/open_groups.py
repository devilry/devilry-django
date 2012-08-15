from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient



class TestRestOpenGroups(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p0:begins(-10):ends(2)',
                                     'p1:begins(-1)',
                                     'p2:begins(5)'],
                            assignments=['a1'])
        self.testhelper.create_user('testuser')
        self.url = '/devilry_student/rest/open-groups/'

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_open_groups_empty(self):
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])

    def test_open_groups(self):

        # Add 3 to the active period, but close one of the groups
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g3:candidate(student1).d1')
        self.testhelper.sub_p1_a1_g1.is_open = False
        self.testhelper.sub_p1_a1_g1.save()

        # Add to the past and the future periods (should not show up)
        self.testhelper.add_to_path('uni;sub.p0.a1.gX:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p2.a1.gY:candidate(student1).d1')

        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        groupnames = set([group['name'] for group in content])
        self.assertEquals(groupnames, set(['g2', 'g3']))
