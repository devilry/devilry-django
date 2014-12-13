import re
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_qualifiesforexam.models import Status
from devilry.devilry_qualifiesforexam.views import StatusPrintView
from devilry.devilry_qualifiesforexam.views import extract_lastname
from devilry.devilry_qualifiesforexam.views import cmp_lastname


class TestStatusPrintView(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, status_id):
        return reverse('devilry_qualifiesforexam_statusprint', kwargs={'status_id': status_id})

    def _getas(self, username, status_id, data={}):
        self.client.login(username=username, password='test')
        return self.client.get(self._get_url(status_id), data)

    def test_status_not_found(self):
        response = self._getas('superuser', 1)
        self.assertEqual(response.status_code, 404)

    def test_status_forbidden(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        self.testhelper.create_user('nobody')
        response = self._getas('nobody', status.pk)
        self.assertEqual(response.status_code, 403)

    def test_status_not_ready(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.NOTREADY)
        response = self._getas('superuser', status.pk)
        self.assertEqual(response.status_code, 404)

    def test_status_periodadmin(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        response = self._getas('periodadmin', status.pk)
        self.assertEqual(response.status_code, 200)

    def test_status_superuser(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'])
        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        response = self._getas('superuser', status.pk)
        self.assertEqual(response.status_code, 200)



    def test_extract_lastname(self):
        self.assertEqual(extract_lastname(self.testhelper.create_user('unused_a', None)), '')
        self.assertEqual(extract_lastname(self.testhelper.create_user('unused_b', ' ')), '')
        self.assertEqual(extract_lastname(self.testhelper.create_user('unused_c', 'Test')), 'Test')
        self.assertEqual(extract_lastname(self.testhelper.create_user('unused_d', 'Test User')), 'User')
        self.assertEqual(extract_lastname(self.testhelper.create_user('unused_e', 'My Test User')), 'User')
        self.assertEqual(extract_lastname(User.objects.create(username='unused_x')), '') # NOTE: No user profile

    def test_cmp_lastname(self):
        user_a = self.testhelper.create_user('a', 'User A')
        user_b = self.testhelper.create_user('b', 'User B')
        self.assertEqual(cmp_lastname(user_b, user_a), 1)


    def _create_relateduser(self, username, full_name=''):
        user = self.testhelper.create_user(username, full_name)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user)
        return relstudent

    def test_sortby_username(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'])
        student1 = self._create_relateduser('student1')
        student2 = self._create_relateduser('student2')

        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        status.students.create(relatedstudent=student1, qualifies=True)
        status.students.create(relatedstudent=student2, qualifies=True)
        self.assertEqual(
                [s.relatedstudent for s in StatusPrintView.get_studentstatuses_by_sorter(status, 'username')],
                [student1, student2])

    def test_sortby_name(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'])
        student1 = self._create_relateduser('student1', 'Student Z')
        student2 = self._create_relateduser('student2', 'Student B')

        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        status.students.create(relatedstudent=student1, qualifies=True)
        status.students.create(relatedstudent=student2, qualifies=True)
        self.assertEqual(
                [s.relatedstudent for s in StatusPrintView.get_studentstatuses_by_sorter(status, 'name')],
                [student2, student1])

    def test_sortby_lastname(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'])
        homer = self._create_relateduser('student1', 'Homer Simpson')
        superman = self._create_relateduser('student2', 'Super Man')
        peterparker = self._create_relateduser('student3', 'Peter Parker')

        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        status.students.create(relatedstudent=homer, qualifies=True)
        status.students.create(relatedstudent=superman, qualifies=True)
        status.students.create(relatedstudent=peterparker, qualifies=True)
        self.assertEqual(
                [s.relatedstudent for s in StatusPrintView.get_studentstatuses_by_sorter(status, 'lastname')],
                [superman, peterparker, homer])



    def _extract_by_spanclass(self, html, cssclass):
        return re.findall('<span class="{0}">(.+?)</span>'.format(cssclass), html)

    def test_sortby_view(self):
        self.testhelper.add(nodes='uni',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'])
        student1 = self._create_relateduser('student1', 'Homer Simpson')
        student2 = self._create_relateduser('student2', 'Peter Parker')

        status = Status.objects.create(
                user=self.testhelper.superuser,
                period=self.testhelper.sub_p1,
                status=Status.READY)
        status.students.create(relatedstudent=student1, qualifies=True)
        status.students.create(relatedstudent=student2, qualifies=True)
        response = self._getas('superuser', status.pk, {'sortby': 'lastname'})
        self.assertEqual(response.status_code, 200)
        usernames = self._extract_by_spanclass(response.content, 'fullname')
        self.assertEqual(usernames, ['Peter Parker', 'Homer Simpson'])
