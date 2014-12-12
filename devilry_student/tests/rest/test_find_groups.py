from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient



class TestRestFindGroups(TestCase):
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
        self.url = '/devilry_student/rest/find-groups/'

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_find_groups_empty(self):
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])

    def test_find_groups(self):
        # Add to the past period (should show up)
        self.testhelper.add_to_path('uni;sub.p0.a1.gOld:candidate(student1).d1')

        # Add to the active period (show show up)
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1,student2).d1')

        # Add to the future period (should not show up)
        self.testhelper.add_to_path('uni;sub.p2.a1.gFut:candidate(student1).d1')

        content, response = self._getas('student1', query='sub')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        self.assertEquals(set(content[0].keys()),
                          set(['id', 'name', 'assignment', 'period', 'subject']))
        groupnames = set([group['name'] for group in content])
        self.assertEquals(groupnames, set(['g1', 'g2', 'gOld']))

        content, response = self._getas('student1', query='old')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)

        content, response = self._getas('student1', query='p1 g2')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['name'], 'g2')
