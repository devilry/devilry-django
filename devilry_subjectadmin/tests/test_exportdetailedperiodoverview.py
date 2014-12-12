from django.test import Client
from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper


class TestExportDetailedPeriodOverview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_user('student1', fullname='Student One')
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

    def _getas(self, username, data={}):
        self.client.login(username=username, password='test')
        url = reverse('devilry_subjectadmin_export_period_details', kwargs={'id': self.testhelper.sub_p1.id})
        return self.client.get(url, data)

    def _test_permsas(self, username):
        response = self._getas(username, {'format': 'csv'})
        self.assertEqual(response.status_code, 200)

    def test_perm_as_periodadmin(self):
        self._test_permsas('periodadmin')
    def test_perm_as_nodeadmin(self):
        self._test_permsas('uniadmin')
    def test_perm_as_superuser(self):
        self._test_permsas('superuser')

    def test_getas_nobody(self):
        self.testhelper.create_user('nobody')
        response = self._getas('nobody', {
            'format': 'csv'
        })
        self.assertEqual(response.status_code, 403)


    def _create_relatedstudent(self, username, fullname=None):
        user = getattr(self.testhelper, username, None)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user)
        return relstudent

    def _create_feedbacks(self, *feedbacks):
        for group, feedback in feedbacks:
            self.testhelper.add_delivery(group, {'file.py': ['print ', 'bah']})
            self.testhelper.add_feedback(group, verdict=feedback)

    def _create_testdata(self):
        self._create_relatedstudent('student1', fullname='Student One')
        self._create_relatedstudent('student2')
        self._create_feedbacks(
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 2, 'is_passing_grade': False}),
            (self.testhelper.sub_p1_a2_gstudent1, {'grade': 'B', 'points': 50, 'is_passing_grade': True})
        )
        self._create_feedbacks(
            (self.testhelper.sub_p1_a1_gstudent2, {'grade': 'A', 'points': 52, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a2_gstudent2, {'grade': 'A', 'points': 53, 'is_passing_grade': True})
        )

    def test_export_csv(self):
        self._create_testdata()
        response = self._getas('periodadmin', {
            'format': 'csv'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '\r\n'.join([
            'NAME,USERNAME,a1 (Grade),a1 (Points),a1 (Passing grade),a2 (Grade),a2 (Points),a2 (Passing grade),WARNINGS',
            'Student One,student1,F,2,Failed,B,50,Passed,',
            'name-missing,student2,A,52,Passed,A,53,Passed,',
            ''
        ]))

    def test_export_ooxml(self):
        self._create_testdata()
        response = self._getas('periodadmin', {
            'format': 'xslx'
        })
        self.assertEqual(response.status_code, 200)
