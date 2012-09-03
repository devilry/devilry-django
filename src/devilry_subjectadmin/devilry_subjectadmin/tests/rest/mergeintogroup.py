from django.test import TestCase
from django.db.models import Q

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry.apps.core.models import Delivery



class TestRestMergeIntoGroup(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)'], # 2 months ago 
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1
        self.url = '/devilry_subjectadmin/rest/mergeintogroup/{0}'.format(self.assignment.id)

    def _postas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.url, data)

    def test_post(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1).d1')
        self.testhelper.add_delivery('sub.p1.a1.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        source = self.testhelper.sub_p1_a1_g1

        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student1,student3):examiner(examiner2)')
        target = self.testhelper.sub_p1_a1_g2

        self.assertEquals(self.assignment.assignmentgroups.count(), 2)
        content, response = self._postas('a1admin', {'source_group_id': source.id,
                                                     'target_group_id': target.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['success'], True)
        self.assertEquals(content['target_group_id'], target.id)
        self.assertEquals(content['source_group_id'], source.id)
        self.assertEquals(self.assignment.assignmentgroups.count(), 1)
        merged_target = self.assignment.assignmentgroups.all()[0]
        self.assertEquals(merged_target.candidates.count(), 3)
        self.assertEquals(merged_target.examiners.count(), 2)

    def test_post_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._postas('nobody', {'source_group_id': 1,
                                                    'target_group_id': 1})
        self.assertEquals(response.status_code, 403)

    def test_post_not_found(self):
        content, response = self._postas('a1admin', {'source_group_id': 1000000,
                                                     'target_group_id': 1100000})
        self.assertEquals(response.status_code, 404)
