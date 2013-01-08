from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_qualifiesforexam.pluginhelpers import create_sessionkey


class TestAllApprovedView(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'],
            assignments=['a1', 'a2'],
            assignmentgroups=[
                'gstudent1:candidate(student1):examiner(examiner1)',
                'gstudent2:candidate(student2):examiner(examiner1)'],
            deadlines=['d1:ends(10)']
        )
        self.testhelper.create_superuser('superuser')
        self.client = Client()

    def _getas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_qualifiesforexam_approved_all'), data)

    def _test_getas(self, username):
        response = self._getas(username, {
            'periodid': self.testhelper.sub_p1.id,
            'pluginsessionid': 'tst'
        })
        self.assertEqual(response.status_code, 302)
        previewdata = self.client.session[create_sessionkey('tst')]
        self.assertEqual(previewdata.passing_relatedstudentids, [])

    def test_get_as_periodadmin(self):
        self._test_getas('periodadmin')
    def test_get_as_nodeadmin(self):
        self._test_getas('uniadmin')
    def test_get_as_superuser(self):
        self._test_getas('superuser')

    def test_getas_nobody(self):
        self.testhelper.create_user('nobody')
        response = self._getas('nobody', {
            'periodid': self.testhelper.sub_p1.id
        })
        self.assertEqual(response.status_code, 403)

    def test_get_invalid_period(self):
        response = self._getas('periodadmin', {
            'periodid': 1000
        })
        self.assertEqual(response.status_code, 403)

    def _create_relatedstudent(self, username):
        user = getattr(self.testhelper, username, None)
        if not user:
            user = self.testhelper.create_user(username)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user)
        return relstudent

    def _create_feedbacks(self, *feedbacks):
        for group, feedback in feedbacks:
            self.testhelper.add_delivery(group, {'file.py': ['print ', 'bah']})
            self.testhelper.add_feedback(group, verdict=feedback)

    def test_realistic(self):
        self._create_relatedstudent('student1')
        relatedStudent2 = self._create_relatedstudent('student2')
        self._create_feedbacks( # Fails because of the F
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': False}),
            (self.testhelper.sub_p1_a2_gstudent1, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        self._create_feedbacks( # Passes all
            (self.testhelper.sub_p1_a1_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a2_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        response = self._getas('periodadmin', {
            'periodid': self.testhelper.sub_p1.id,
            'pluginsessionid': 'tst'
        })
        self.assertEqual(response.status_code, 302)
        previewdata = self.client.session[create_sessionkey('tst')]
        self.assertEqual(previewdata.passing_relatedstudentids, [relatedStudent2.id])