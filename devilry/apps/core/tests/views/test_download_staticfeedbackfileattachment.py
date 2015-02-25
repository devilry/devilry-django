from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from devilry.project.develop.testhelpers.corebuilder import AssignmentGroupBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class TestDownloadStaticFeedbackFileAttachmentView(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.teststudent = UserBuilder('teststudent').user
        self.fileattachment = AssignmentGroupBuilder\
            .quickadd_ducku_duck1010_active_assignment1_group(studentuser=self.teststudent)\
            .add_examiners(self.testexaminer)\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_passed_A_feedback(saved_by=self.testexaminer)\
            .add_fileattachment(filename='test.txt', filedata='A testfile').fileattachment

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user, pk, **querystring):
        self._login(user)
        url = reverse('devilry_core_feedbackfileattachment', kwargs={
            'pk': pk
        })
        if querystring:
            url = '{}?{}'.format(url, urlencode(querystring))
        return self.client.get(url)

    def test_404_not_owner_or_superuser_or_candidate(self):
        response = self._get_as(UserBuilder('otheruser').user, self.fileattachment.id)
        self.assertEquals(response.status_code, 404)

    def test_404_not_found(self):
        response = self._get_as(self.testexaminer, 10001)
        self.assertEquals(response.status_code, 404)

    def _test_as(self, user):
        response = self._get_as(user, self.fileattachment.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['content-type'], 'text/plain')
        self.assertEquals(response.content, 'A testfile')
        self.assertNotIn('content-disposition', response)

    def test_ok_as_superuser(self):
        self._test_as(UserBuilder('superuser', is_superuser=True).user)

    def test_ok_as_examiner(self):
        self._test_as(self.testexaminer)

    def test_ok_as_student(self):
        self._test_as(self.teststudent)

    def test_download_content_disposition(self):
        response = self._get_as(self.testexaminer, self.fileattachment.id, download='yes')
        self.assertEquals(response.status_code, 200)
        self.assertIn('content-disposition', response)
        self.assertEquals(response['content-disposition'], 'attachment; filename=test.txt')
