import json
from tempfile import mkdtemp
from shutil import rmtree
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry_student.models import UploadedDeliveryFile
from devilry.project.develop.testhelpers.login import LoginTestCaseMixin



class TestUploadDeliveryFile(TestCase, LoginTestCaseMixin):

    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.mediaroot = mkdtemp()

    def tearDown(self):
        rmtree(self.mediaroot)

    def _get_url(self, deadline_id):
        return reverse('devilry_student_upload_deliveryfile', args=[deadline_id])

    def test_post_not_authenticated(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
                .add_assignment('week1')\
                .add_group(students=[self.testuser])\
                .add_deadline_x_weeks_ago(weeks=1).deadline

            response = self.client.post(self._get_url(deadline.id), {
                'files': SimpleUploadedFile('testname.txt', 'test')
            })
            self.assertEqual(response.status_code, 401)
            self.assertEqual(UploadedDeliveryFile.objects.count(), 0)

    def test_post_not_candidate(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
                .add_assignment('week1')\
                .add_group()\
                .add_deadline_x_weeks_ago(weeks=1).deadline
            response = self.post_as(self.testuser, self._get_url(deadline.id), {})
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertFalse(content['success'])
            self.assertEquals(content['error'], 'User not Candidate on requested group.')

    def test_post_deeadline_does_not_exist(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            response = self.post_as(self.testuser, self._get_url(1000001), {})
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertFalse(content['success'])
            self.assertEquals(content['error'], 'Deadline not found.')

    def test_post_no_files(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
                .add_assignment('week1')\
                .add_group(students=[self.testuser])\
                .add_deadline_x_weeks_ago(weeks=1).deadline
            response = self.post_as(self.testuser, self._get_url(deadline.id), {})
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertFalse(content['success'])
            self.assertEquals(content['error'], 'No files attached.')

    def test_post(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
                .add_assignment('week1')\
                .add_group(students=[self.testuser])\
                .add_deadline_x_weeks_ago(weeks=1).deadline
            response = self.post_as(self.testuser, self._get_url(deadline.id), {
                'files': SimpleUploadedFile('testname.txt', 'test')
            })
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertTrue(content['success'])
            self.assertEquals(len(content['uploads']), 1)
            self.assertEquals(content['uploads'][0]['filename'], 'testname.txt')
            self.assertEqual(UploadedDeliveryFile.objects.count(), 1)
            uploadedfile = UploadedDeliveryFile.objects.all()[0]
            self.assertEquals(uploadedfile.filename, 'testname.txt')
            self.assertEquals(uploadedfile.uploaded_file.read(), 'test')

    def test_post_multiple(self):
        with self.settings(MEDIA_ROOT=self.mediaroot):
            deadline = PeriodBuilder.quickadd_ducku_duck1010_active()\
                .add_assignment('week1')\
                .add_group(students=[self.testuser])\
                .add_deadline_x_weeks_ago(weeks=1).deadline
            response = self.post_as(self.testuser, self._get_url(deadline.id), {
                'files': [
                    SimpleUploadedFile('testname.txt', 'test'),
                    SimpleUploadedFile('testname2.txt', 'test2')
                ]
            })
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertTrue(content['success'])
            self.assertEquals(len(content['uploads']), 2)
            self.assertEquals(content['uploads'][0]['filename'], 'testname.txt')
            self.assertEquals(content['uploads'][1]['filename'], 'testname2.txt')
            self.assertEqual(UploadedDeliveryFile.objects.count(), 2)
            filenames = [f.filename for f in UploadedDeliveryFile.objects.all()]
            self.assertEquals(set(filenames), set(['testname.txt', 'testname2.txt']))
