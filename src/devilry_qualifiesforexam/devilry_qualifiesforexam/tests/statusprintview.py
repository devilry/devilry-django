from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_qualifiesforexam.models import Status


class TestStatusPrintView(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, status_id):
        return reverse('devilry_qualifiesforexam_statusprint', kwargs={'status_id': status_id})

    def _getas(self, username, status_id):
        self.client.login(username=username, password='test')
        return self.client.get(self._get_url(status_id))

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
