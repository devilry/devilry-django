from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_qualifiesforexam.pluginhelpers import create_sessionkey
from devilry.devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginTestMixin
from devilry.devilry_qualifiesforexam.models import Status
from devilry.devilry_qualifiesforexam_approved.post_statussave import post_statussave_subset
from devilry.devilry_qualifiesforexam_approved.models import SubsetPluginSetting
from devilry.devilry_qualifiesforexam.pluginhelpers import PluginResultsFailedVerification


class TestAllApprovedView(TestCase, QualifiesForExamPluginTestMixin):
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
        self.period = self.testhelper.sub_p1
        self.client = Client()

    def _getas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_qualifiesforexam_approved_all'), data)

    def _test_permsas(self, username):
        response = self._getas(username, {
            'periodid': self.testhelper.sub_p1.id,
            'pluginsessionid': 'tst'
        })
        self.assertEqual(response.status_code, 302)
        previewdata = self.client.session[create_sessionkey('tst')]
        self.assertEqual(previewdata['passing_relatedstudentids'], [])

    def test_perms_as_periodadmin(self):
        self._test_permsas('periodadmin')
    def test_perms_as_nodeadmin(self):
        self._test_permsas('uniadmin')
    def test_perms_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        self._test_permsas('superuser')

    def test_perms_as_nobody(self):
        self.testhelper.create_user('nobody')
        response = self._getas('nobody', {
            'periodid': self.testhelper.sub_p1.id
        })
        self.assertEqual(response.status_code, 403)

    def test_invalid_period(self):
        response = self._getas('periodadmin', {
            'periodid': 1000
        })
        self.assertEqual(response.status_code, 403)

    def test_realistic(self):
        self.create_relatedstudent('student1')
        relatedStudent2 = self.create_relatedstudent('student2')
        self.create_feedbacks( # Fails because of the F
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': False}),
            (self.testhelper.sub_p1_a2_gstudent1, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        self.create_feedbacks( # Passes all
            (self.testhelper.sub_p1_a1_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a2_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        response = self._getas('periodadmin', {
            'periodid': self.testhelper.sub_p1.id,
            'pluginsessionid': 'tst'
        })
        self.assertEqual(response.status_code, 302)
        previewdata = self.client.session[create_sessionkey('tst')]
        self.assertEqual(previewdata['passing_relatedstudentids'], [relatedStudent2.id])

    def test_verify(self):
        status = Status(period=self.period, status='ready', message='',
            user=self.testhelper.periodadmin,
            plugin='devilry_qualifiesforexam_approved.subset'
        )
        status.save()
        relatedStudent1 = self.create_relatedstudent('student1')
        status.students.create(relatedstudent=relatedStudent1, qualifies=True)

        self.create_feedbacks(
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': False})
        )

        with self.assertRaises(PluginResultsFailedVerification):
            post_statussave_subset(status, {
                'assignmentids_that_must_be_passed': [self.testhelper.sub_p1_a1.id]
            })


class TestSubsetApprovedView(TestCase, QualifiesForExamPluginTestMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'],
            assignments=['a1:ln(Assignment One)', 'a2:ln(Assignment Two)', 'a3:ln(Assignment Three)'],
            assignmentgroups=[
                'gstudent1:candidate(student1):examiner(examiner1)',
                'gstudent2:candidate(student2):examiner(examiner1)',
                'gstudent3:candidate(student3):examiner(examiner1)',
            ],
            deadlines=['d1:ends(10)']
        )
        self.period = self.testhelper.sub_p1
        self.client = Client()

    def _getas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_qualifiesforexam_approved_subset'), data)

    def _postas(self, username, data, querystring):
        self.client.login(username=username, password='test')
        from urllib import urlencode
        url = '{0}?{1}'.format(
            reverse('devilry_qualifiesforexam_approved_subset'),
            urlencode(querystring))
        return self.client.post(url, data)


    def _test_perms_as(self, username):
        querystring = {'periodid': self.testhelper.sub_p1.id, 'pluginsessionid': 'tst'}
        response = self._getas(username, querystring)
        self.assertEqual(response.status_code, 200)

        response = self._postas(username,
            data = {'assignments': [str(self.testhelper.sub_p1_a1.id)]},
            querystring = querystring)
        self.assertEqual(response.status_code, 302)

    def test_perms_as_periodadmin(self):
        self._test_perms_as('periodadmin')
    def test_perms_as_nodeadmin(self):
        self._test_perms_as('uniadmin')
    def test_perms_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        self._test_perms_as('superuser')

    def test_perms_as_nobody(self):
        self.testhelper.create_user('nobody')
        querystring = {'periodid': self.testhelper.sub_p1.id}
        response = self._getas('nobody', querystring)
        self.assertEqual(response.status_code, 403)
        response = self._postas('nobody', data = {}, querystring=querystring)
        self.assertEqual(response.status_code, 403)

    def test_invalid_period(self):
        querystring = {'periodid': 1000}
        response = self._getas('periodadmin', querystring)
        self.assertEqual(response.status_code, 403)
        response = self._postas('nobody', data = {}, querystring=querystring)
        self.assertEqual(response.status_code, 403)

    def test_get_formrendered(self):
        self.testhelper.add_to_path('uni;sub.p2:admin(periodadmin).test:ln(Test Assignment)')
        querystring = {'periodid': self.testhelper.sub_p1.id, 'pluginsessionid': 'tst'}
        response = self._getas('periodadmin', querystring)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Assignment One', response.content)
        self.assertIn('Assignment Two', response.content)
        self.assertIn('Assignment Three', response.content)
        self.assertNotIn('Test Assignment', response.content)

    def test_post_realistic(self):
        self.create_relatedstudent('student1')
        relatedStudent2 = self.create_relatedstudent('student2')
        relatedStudent3 = self.create_relatedstudent('student3')
        self.create_feedbacks( # student1 Fails because of the F on a1 and a2
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': False}),
            (self.testhelper.sub_p1_a2_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a3_gstudent1, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        self.create_feedbacks( # student2 Passes all
            (self.testhelper.sub_p1_a1_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a2_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a3_gstudent2, {'grade': 'A', 'points': 0, 'is_passing_grade': True})
        )
        self.create_feedbacks( # student3 passes a1 and a2, so he passes
            (self.testhelper.sub_p1_a1_gstudent3, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a2_gstudent3, {'grade': 'A', 'points': 0, 'is_passing_grade': True}),
            (self.testhelper.sub_p1_a3_gstudent3, {'grade': 'F', 'points': 0, 'is_passing_grade': False})
        )
        response = self._postas('periodadmin',
            data = {
                'assignments': [str(self.testhelper.sub_p1_a1.id)]},
            querystring = {
                'periodid': self.testhelper.sub_p1.id,
                'pluginsessionid': 'tst'}
        )
        self.assertEqual(response.status_code, 302)
        previewdata = self.client.session[create_sessionkey('tst')]
        self.assertEqual(
            set(previewdata['passing_relatedstudentids']),
            set([relatedStudent2.id, relatedStudent3.id]))

    def test_save_settings(self):
        status = Status(period=self.period, status='ready', message='',
            user=self.testhelper.periodadmin,
            plugin='devilry_qualifiesforexam_approved.subset'
        )
        status.save()
        self.assertEqual(SubsetPluginSetting.objects.count(), 0)
        post_statussave_subset(status, {
            'assignmentids_that_must_be_passed': [self.testhelper.sub_p1_a1.id, self.testhelper.sub_p1_a2.id]
        })
        self.assertEqual(SubsetPluginSetting.objects.count(), 1)
        settings = status.devilry_qualifiesforexam_approved_subsetpluginsetting
        self.assertEqual(settings.selectedassignment_set.count(), 2)
        ids = set([selected.assignment.id for selected in settings.selectedassignment_set.all()])
        self.assertEqual(ids, set([self.testhelper.sub_p1_a1.id, self.testhelper.sub_p1_a2.id]))

    def test_verify(self):
        status = Status(period=self.period, status='ready', message='',
            user=self.testhelper.periodadmin,
            plugin='devilry_qualifiesforexam_approved.subset'
        )
        status.save()
        relatedStudent1 = self.create_relatedstudent('student1')
        status.students.create(relatedstudent=relatedStudent1, qualifies=True)

        self.create_feedbacks(
            (self.testhelper.sub_p1_a1_gstudent1, {'grade': 'F', 'points': 0, 'is_passing_grade': False})
        )

        with self.assertRaises(PluginResultsFailedVerification):
            post_statussave_subset(status, {
                'assignmentids_that_must_be_passed': [self.testhelper.sub_p1_a1.id]
            })
