import unittest
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from devilry.project.develop.testhelpers.corebuilder import AssignmentGroupBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_gradingsystem.models import FeedbackDraftFile


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestDownloadFeedbackDraftFileView(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.deliverybuilder = AssignmentGroupBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group()\
            .add_examiners(self.testexaminer)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        self.draftfile = FeedbackDraftFile(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        self.draftfile.file.save('test.txt', ContentFile('A testfile'))

    def _login(self, user):
        self.client.login(username=user.shortname, password='test')

    def _get_as(self, user, pk, **querystring):
        self._login(user)
        url = reverse('devilry_gradingsystem_feedbackdraftfile', kwargs={
            'pk': pk
        })
        if querystring:
            url = '{}?{}'.format(url, urlencode(querystring))
        return self.client.get(url)

    def test_403_not_owner_or_superuser(self):
        response = self._get_as(UserBuilder('otheruser').user, self.draftfile.id)
        self.assertEquals(response.status_code, 403)

    def test_404_not_found(self):
        response = self._get_as(self.testexaminer, 10001)
        self.assertEquals(response.status_code, 404)

    def _test_as(self, user):
        response = self._get_as(user, self.draftfile.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['content-type'], 'text/plain')
        self.assertEquals(response.content, 'A testfile')
        self.assertNotIn('content-disposition', response)

    def test_ok_as_owner(self):
        self._test_as(self.testexaminer)

    def test_ok_as_superuser(self):
        self._test_as(UserBuilder('superuser', is_superuser=True).user)

    def test_download_content_disposition(self):
        response = self._get_as(self.testexaminer, self.draftfile.id, download='yes')
        self.assertEquals(response.status_code, 200)
        self.assertIn('content-disposition', response)
        self.assertEquals(response['content-disposition'], 'attachment; filename=test.txt')
