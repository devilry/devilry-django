from datetime import datetime
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
                                     'p1:begins(-2):ends(6)',
                                     'p2:begins(5)'],
                            assignments=['a1'])
        self.testhelper.create_user('testuser')
        self.url = '/devilry_student/rest/open-groups/'

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

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

    def test_open_groups_nonelectronic(self):

        # Add 3 to the active period, but close one of the groups
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a2.g2:candidate(student1).d1')
        self.testhelper.sub_p1_a1.delivery_types = 1
        self.testhelper.sub_p1_a1.save()

        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['name'], 'g2')

    def test_deadline_expired_and_order(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1:ends(1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1).d1:ends(70)')
        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
        self.assertEquals(content[0]['name'], 'g1')
        self.assertEquals(content[0]['active_deadline']['deadline_expired'], True)
        self.assertEquals(content[1]['name'], 'g2')
        self.assertEquals(content[1]['active_deadline']['deadline_expired'], False)

    def test_only_deadline_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1:ends(1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1).d1:ends(70)')
        content, response = self._getas('student1', only='deadline_expired')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['name'], 'g1')
        self.assertEquals(content[0]['active_deadline']['deadline_expired'], True)

    def test_only_deadline_not_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1:ends(1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1).d1:ends(70)')
        content, response = self._getas('student1', only='deadline_not_expired')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['name'], 'g2')
        self.assertEquals(content[0]['active_deadline']['deadline_expired'], False)

    def test_hard_deadlines(self):
        # Add 2 assignments to the active period:
        # - one hard
        #   - 2 groups, one after deadline
        # - one soft
        #   - 2 groups, one after deadline
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1') # Expired deadline
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1).d1:ends(80)') # In the future
        self.testhelper.add_to_path('uni;sub.p1.a2.g3:candidate(student1).d1') # Expired deadline
        self.testhelper.add_to_path('uni;sub.p1.a2.g4:candidate(student1).d1:ends(80)') # In the future
        self.assertTrue(self.testhelper.sub_p1_a1_g1_d1.deadline < datetime.now())
        self.assertTrue(self.testhelper.sub_p1_a1_g2_d1.deadline > datetime.now())
        self.assertTrue(self.testhelper.sub_p1_a2_g3_d1.deadline < datetime.now())
        self.assertTrue(self.testhelper.sub_p1_a2_g4_d1.deadline > datetime.now())
        self.testhelper.sub_p1_a2.deadline_handling = 1 # Hard deadlines on a2
        self.testhelper.sub_p1_a2.save()

        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        groupnames = set([group['name'] for group in content])
        self.assertEquals(groupnames, set(['g1', 'g2', 'g4']))
