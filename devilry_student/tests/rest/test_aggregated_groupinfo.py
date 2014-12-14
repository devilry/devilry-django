from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder



class TestRestAggregatedGroupInfo(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1)'],
                            assignments=['a1'])
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1).d1:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d2:ends(10)')
        self.group = self.testhelper.sub_p1_a1_g1
        self.url = '/devilry_student/rest/aggregated-groupinfo/{0}'.format(self.group.id)

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody')
        self.assertEquals(response.status_code, 403)

    def test_groupinfo(self):
        content, response = self._getas('student1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(set(content.keys()),
                          set(['id', 'name', 'is_open', 'candidates', 'examiners',
                               'deadlines', 'active_feedback', 'status',
                               'deadline_handling', 'breadcrumbs', 'delivery_types',
                               'is_relatedstudent_on_period', 'students_can_create_groups_now']))
        self.assertEquals(content['id'], self.group.id)
        self.assertEquals(content['name'], 'g1')
        self.assertEquals(content['is_open'], True)
        self.assertEquals(content['deadline_handling'], 0)
        self.assertEquals(content['active_feedback'], None)
        self.assertEquals(content['delivery_types'], 0)
        self.assertEquals(content['is_relatedstudent_on_period'], False)

    def test_candidates(self):
        content, response = self._getas('student1')
        candidates = content['candidates']
        self.assertEquals(len(candidates), 2)
        self.assertEquals(set(candidates[0].keys()),
                          set(['id', 'candidate_id', 'identifier', 'user']))
        self.assertEquals(set(candidates[0]['user'].keys()),
                          set(['id', 'username', 'email', 'full_name', 'displayname']))

    def test_examiners(self):
        content, response = self._getas('student1')
        examiners = content['examiners']
        self.assertEquals(len(examiners), 1)
        self.assertEquals(set(examiners[0].keys()),
                          set(['id', 'user']))
        self.assertEquals(set(examiners[0]['user'].keys()),
                          set(['id', 'username', 'email', 'full_name', 'displayname']))
        self.assertEquals(examiners[0]['user']['username'], 'examiner1')

    def test_examiners_anonymous(self):
        self.group.parentnode.anonymous = True
        self.group.parentnode.save()
        content, response = self._getas('student1')
        examiners = content['examiners']
        self.assertEquals(examiners, None)

    def test_students_can_create_groups_now_true(self):
        self.group.parentnode.students_can_create_groups = True
        self.group.parentnode.save()
        content, response = self._getas('student1')
        self.assertTrue(content['students_can_create_groups_now'])

    def test_students_can_create_groups_now_false(self):
        self.group.parentnode.students_can_create_groups = False
        self.group.parentnode.save()
        content, response = self._getas('student1')
        self.assertFalse(content['students_can_create_groups_now'])

    def test_students_can_create_groups_now_true_and_future(self):
        self.group.parentnode.students_can_create_groups = True
        self.group.parentnode.students_can_not_create_groups_after = DateTimeBuilder.now().plus(days=2)
        self.group.parentnode.save()
        content, response = self._getas('student1')
        self.assertTrue(content['students_can_create_groups_now'])

    def test_students_can_create_groups_now_true_and_future(self):
        self.group.parentnode.students_can_create_groups = True
        self.group.parentnode.students_can_not_create_groups_after = DateTimeBuilder.now().minus(days=2)
        self.group.parentnode.save()
        content, response = self._getas('student1')
        self.assertFalse(content['students_can_create_groups_now'])

    def test_deadlines(self):
        content, response = self._getas('student1')
        deadlines = content['deadlines']
        self.assertEquals(len(deadlines), 2)
        self.assertEquals(set(deadlines[0].keys()),
                          set(['id', 'deadline', 'deliveries', 'text',
                               'offset_from_now', 'in_the_future']))

    def test_breadcrumbs(self):
        content, response = self._getas('student1')
        breadcrumbs = content['breadcrumbs']
        self.assertEquals(breadcrumbs,
                          {u'assignment': {u'id': self.group.parentnode.id,
                                           u'long_name': u'A1',
                                           u'short_name': u'a1'},
                           u'period': {u'id': self.group.parentnode.parentnode.id,
                                       u'long_name': u'P1',
                                       u'short_name': u'p1'},
                           u'subject': {u'id': self.group.parentnode.parentnode.parentnode.id,
                                        u'long_name': u'Sub',
                                        u'short_name': u'sub'}})

    def test_is_relatedstudent_on_period(self):
        self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        content, response = self._getas('student1')
        registred = content['is_relatedstudent_on_period']
        self.assertEquals(registred, True)
