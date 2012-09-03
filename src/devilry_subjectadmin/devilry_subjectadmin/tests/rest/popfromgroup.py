from django.test import TestCase
from django.db.models import Q

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry.apps.core.models import Delivery



class TestRestPopFromGroup(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)'], # 2 months ago 
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1
        self.url = '/devilry_subjectadmin/rest/popfromgroup/{0}'.format(self.assignment.id)

    def _putas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self.url, data)

    def test_put(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1).d1')
        self.testhelper.add_delivery('sub.p1.a1.g1', {'bad.py': ['print ', 'bah']})
        self.testhelper.add_feedback('sub.p1.a1.g1', verdict={'grade': 'F', 'points': 30, 'is_passing_grade': False})
        source = self.testhelper.sub_p1_a1_g1
        student1cand = source.candidates.get(student=self.testhelper.student1)

        self.assertEquals(self.assignment.assignmentgroups.count(), 1)
        content, response = self._putas('a1admin', {'group_id': source.id,
                                                    'candidate_id': student1cand.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.assignment.assignmentgroups.count(), 2)
        self.assertEquals(content['success'], True)
        self.assertEquals(content['group_id'], source.id)
        self.assertNotEquals(content['new_group_id'], source.id)
        self.assertEquals(source.candidates.count(), 1)
        self.assertEquals(source.candidates.all()[0].student.username, 'student2')

        newgroup = self.assignment.assignmentgroups.get(~Q(id=source.id))
        self.assertEquals(content['new_group_id'], newgroup.id)
        self.assertEquals(newgroup.candidates.count(), 1)
        self.assertEquals(newgroup.candidates.all()[0].student.username, 'student1')

        # Some sanity tests. Note that all of this is already tested in the tests for AssignmentGroup.pop_candidate
        def get_delivery(group):
            return Delivery.objects.get(deadline__assignment_group=group)
        delivery = get_delivery(source)
        newdelivery = get_delivery(newgroup)
        self.assertEquals(delivery.time_of_delivery, newdelivery.time_of_delivery)
        self.assertEquals(delivery.feedbacks.all()[0].grade,
                          newdelivery.feedbacks.all()[0].grade)
        self.assertEquals(newdelivery.feedbacks.all()[0].grade, 'F')

    def test_put_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._putas('nobody', {'group_id': 1,
                                                    'candidate_id': 1})
        self.assertEquals(response.status_code, 403)
