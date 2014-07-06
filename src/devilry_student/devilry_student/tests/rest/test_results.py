from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry_qualifiesforexam.models import Status



class TestRestResults(TestCase):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p0:begins(-10):ends(2)',
                                     'p1:begins(-2):ends(6)',
                                     'p2:begins(5)'],
                            assignments=['a1:pub(1)', 'a2:pub(2)', 'a3:pub(3)'])
        self.testhelper.create_user('testuser')
        self.url = reverse('devilry_student-rest-results')

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_get_empty(self):
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content, [])


    def test_get_hierarchy(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')

        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(subjects), 1)
        self.assertEquals(subjects[0]['id'], self.testhelper.sub.id)
        self.assertEquals(subjects[0]['short_name'], self.testhelper.sub.short_name)
        self.assertEquals(subjects[0]['long_name'], self.testhelper.sub.long_name)

        periods = subjects[0]['periods']
        self.assertEquals(len(periods), 1)
        self.assertEquals(periods[0]['id'], self.testhelper.sub_p1.id)
        self.assertEquals(periods[0]['short_name'], self.testhelper.sub_p1.short_name)
        self.assertEquals(periods[0]['long_name'], self.testhelper.sub_p1.long_name)
        self.assertEquals(periods[0]['is_relatedstudent'], False)

        assignments = periods[0]['assignments']
        self.assertEquals(len(assignments), 1)
        self.assertEquals(assignments[0]['id'], self.testhelper.sub_p1_a1.id)
        self.assertEquals(assignments[0]['short_name'], self.testhelper.sub_p1_a1.short_name)
        self.assertEquals(assignments[0]['long_name'], self.testhelper.sub_p1_a1.long_name)

        groups = assignments[0]['groups']
        self.assertEquals(len(groups), 1)
        self.assertEquals(groups[0]['id'], self.testhelper.sub_p1_a1_g1.id)

    def test_get_groupdetails_corrected(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')
        delivery1 = self.testhelper.add_delivery('sub.p1.a1.g1', {'x.txt': ['x']})
        self.testhelper.add_feedback(delivery1, verdict={'grade': 'C', 'points': 55, 'is_passing_grade': True})

        content , response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        group = subjects[0]['periods'][0]['assignments'][0]['groups'][0]
        self.assertEquals(group['id'], self.testhelper.sub_p1_a1_g1.id)
        self.assertEquals(group['status'], 'corrected')

        self.assertIsNotNone(group['feedback'])
        self.assertEquals(group['feedback']['grade'], 'C')
        self.assertEquals(group['feedback']['is_passing_grade'], True)
        self.assertNotIn('points', group['feedback'])

    def test_get_groupdetails_not_corrected(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')
        delivery1 = self.testhelper.add_delivery('sub.p1.a1.g1', {'x.txt': ['x']})

        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        group = subjects[0]['periods'][0]['assignments'][0]['groups'][0]
        self.assertEquals(group['id'], self.testhelper.sub_p1_a1_g1.id)
        self.assertEquals(group['status'], 'waiting-for-feedback')
        self.assertIsNone(group['feedback'])

    def test_get_ordering_assignments(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a2.g1:candidate(student1):examiner(examiner1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a3.g1:candidate(student1):examiner(examiner1).d1')
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        assignments = subjects[0]['periods'][0]['assignments']
        self.assertEquals(len(assignments), 3)
        self.assertEquals(assignments[2]['id'], self.testhelper.sub_p1_a1.id)
        self.assertEquals(assignments[1]['id'], self.testhelper.sub_p1_a2.id)
        self.assertEquals(assignments[0]['id'], self.testhelper.sub_p1_a3.id)

    def test_all_ordering_periods(self):
        self.testhelper.add_to_path('uni;sub.p0.a1.gX:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        periods = subjects[0]['periods']
        self.assertEquals(len(periods), 2)
        self.assertEquals(periods[1]['id'], self.testhelper.sub_p0.id)
        self.assertEquals(periods[0]['id'], self.testhelper.sub_p1.id)

    def test_activeonly(self):
        self.testhelper.add_to_path('uni;sub.p0.a1.gX:candidate(student1).d1') # Not active
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p2.a1.gY:candidate(student1).d1') # Not included because it is not published
        content, response = self._getas('student1', activeonly='true')
        subjects = content
        self.assertEquals(response.status_code, 200)
        periods = subjects[0]['periods']
        self.assertEquals(len(periods), 1)
        self.assertEquals(periods[0]['id'], self.testhelper.sub_p1.id)

    def test_all_published_periods(self):
        self.testhelper.add_to_path('uni;sub.p0.a1.gX:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p2.a1.gY:candidate(student1).d1') # Not included because it is not published
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        periods = subjects[0]['periods']
        self.assertEquals(len(periods), 2)
        self.assertEquals(set([p['short_name'] for p in periods]),
            set(['p0', 'p1']))

    def test_perms_owner_only(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2).d1')
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        groups = subjects[0]['periods'][0]['assignments'][0]['groups']
        self.assertEquals(len(groups), 1)
        self.assertEquals(groups[0]['id'], self.testhelper.sub_p1_a1_g1.id)

    def test_get_qualifiesforexam_true(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        status = Status.objects.create(period=self.testhelper.sub_p1,
                user=self.testhelper.testuser,
                status=Status.READY)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        status.students.create(relatedstudent=relstudent, qualifies=True)

        content , response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        period = subjects[0]['periods'][0]
        self.assertTrue(period['qualifiesforexams'])

    def test_get_qualifiesforexam_false(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        status = Status.objects.create(period=self.testhelper.sub_p1,
                user=self.testhelper.testuser,
                status=Status.READY)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        status.students.create(relatedstudent=relstudent, qualifies=False)

        content , response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        period = subjects[0]['periods'][0]
        self.assertFalse(period['qualifiesforexams'])

    def test_get_qualifiesforexam_none(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        period = subjects[0]['periods'][0]
        self.assertIsNone(period['qualifiesforexams'])

    def test_get_qualifiesforexam_notready(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        status = Status.objects.create(period=self.testhelper.sub_p1,
                user=self.testhelper.testuser,
                status=Status.NOTREADY)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        status.students.create(relatedstudent=relstudent, qualifies=False)

        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        period = subjects[0]['periods'][0]
        self.assertIsNone(period['qualifiesforexams'])


    def test_get_is_relatedstudent(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        content, response = self._getas('student1')
        subjects = content
        self.assertEquals(response.status_code, 200)
        p1 = subjects[0]['periods'][0]
        self.assertEquals(p1['is_relatedstudent'], True)
