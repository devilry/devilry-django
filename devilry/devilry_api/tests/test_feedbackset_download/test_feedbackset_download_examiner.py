import os
import shutil
from StringIO import StringIO
from zipfile import ZipFile

from django.core.files.base import ContentFile
from django.test import TestCase
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core import mommy_recipes
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_api.feedbackset_download.views.feedbackset_download_examiner import ExaminerFeedbacksetView
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class SetUpTearDown(TestCase):

    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        AssignmentGroupDbCacheCustomSql().initialize()
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree(self.backend_path, ignore_errors=True)


class TestFeedbacksetDownloadExaminerPermission(test_common_mixins.TestReadOnlyPermissionMixin,
                                                test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                                                api_test_helper.TestCaseMixin,
                                                APITestCase):
    viewclass = ExaminerFeedbacksetView


class TestFeedbacksetDownloadExaminer(api_test_helper.TestCaseMixin, SetUpTearDown):

    viewclass = ExaminerFeedbacksetView

    def test_cannot_download_files_examiner_not_in_group_404(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            # Test download files from feedbackset
            group = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE))
            testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
            # Add student comment with file
            testcomment_student = mommy.make('devilry_group.GroupComment',
                                             feedback_set=testfeedbackset,
                                             user_role='student')
            commentfile_student = mommy.make('devilry_comment.CommentFile',
                                             comment=testcomment_student,
                                             filename='testfile-student.txt')
            commentfile_student.file.save('testfile.txt', ContentFile('student-testcontent'))

            examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
            apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
            response = self.mock_get_request(content_id=testfeedbackset.id, apikey=apikey.key)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data['detail'], 'Feedbackset not found')

    def test_feedbackset_files_download_before_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            # Test download files from feedbackset
            group = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE))
            testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
            # Add student comment with file
            testcomment_student = mommy.make('devilry_group.GroupComment',
                                             feedback_set=testfeedbackset,
                                             user_role='student')
            commentfile_student = mommy.make('devilry_comment.CommentFile',
                                             comment=testcomment_student,
                                             filename='testfile-student.txt')
            commentfile_student.file.save('testfile.txt', ContentFile('student-testcontent'))

            examiner = core_mommy.examiner(group=group)
            apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
            response = self.mock_get_request(content_id=testfeedbackset.id, apikey=apikey.key)
            self.assertEqual(response.status_code, 200)
            zipfileobject = ZipFile(StringIO(response.content))
            self.assertEquals('student-testcontent', zipfileobject.read('delivery/testfile-student.txt'))

    def test_feedbackset_files_download_after_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            # Test download files from feedbackset
            group = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
            testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
            # Add student comment with file
            testcomment_student = mommy.make('devilry_group.GroupComment',
                                             feedback_set=testfeedbackset,
                                             user_role='student')
            commentfile_student = mommy.make('devilry_comment.CommentFile',
                                             comment=testcomment_student,
                                             filename='testfile-student.txt')
            commentfile_student.file.save('testfile.txt', ContentFile('student-testcontent'))

            examiner = core_mommy.examiner(group=group)
            apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
            response = self.mock_get_request(content_id=testfeedbackset.id, apikey=apikey.key)
            self.assertEqual(response.status_code, 200)
            zipfileobject = ZipFile(StringIO(response.content))
            self.assertEquals('student-testcontent', zipfileobject.read('uploaded_after_deadline/testfile-student.txt'))
