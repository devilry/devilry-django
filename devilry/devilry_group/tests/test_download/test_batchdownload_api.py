import json
import shutil
import unittest

import mock
from django import test
from django.conf import settings

from devilry.project.develop.testhelpers import skip_rq_tests
from django.core.files.base import ContentFile
from django.http import Http404
from django.test import override_settings
from django.utils import timezone
from django_cradmin.cradmin_testhelpers import TestCaseMixin
from ievv_opensource.ievv_batchframework import batchregistry
from ievv_opensource.ievv_batchframework.models import BatchOperation
from model_mommy import mommy

from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_dbcache import customsql
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import tasks
from devilry.devilry_group.views.download_files.batch_download_api import BatchCompressionAPIFeedbackSetView


class TestHelper(object):
    """
    Testhelper class for tests.
    """
    def _mock_batchoperation(self, context_object, status):
        """
        Create a batchoperation for the context object passed as argument.
        This way we can easlily set the batchoperation status without running the actual task since the
        api checks the batchoperation status to determine the response data.
        """
        batchoperation = BatchOperation(
            operationtype=BatchCompressionAPIFeedbackSetView.batchoperation_type,
            context_object=context_object,
            status=status)
        batchoperation.save()

    def _mock_batchoperation_status(self, context_object_id, status=BatchOperation.STATUS_UNPROCESSED):
        # helper function
        # Set the BatchOperation.status to the desired status for testing.
        # Defaults to unprocessed.
        batchoperation = BatchOperation.objects.get(context_object_id=context_object_id)
        batchoperation.operationtype = BatchCompressionAPIFeedbackSetView.batchoperation_type
        batchoperation.status = status
        batchoperation.save()

    def _register_and_run_actiongroup(self, actiongroup_name, task, context_object):
        # helper function
        # Shortcut for registering and starting an ActionGroup
        # as this will need to be set up frequently.
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name=actiongroup_name,
                mode=batchregistry.ActionGroup.MODE_ASYNCHRONOUS,
                actions=[
                    task
                ]))
        batchregistry.Registry.get_instance()\
            .run(actiongroup_name=actiongroup_name,
                 context_object=context_object,
                 test='test')


@unittest.skipIf(skip_rq_tests.should_skip_tests_that_require_rq_async(),
                 reason='Tests that require RQ to run async. Disabled if DEVILRY_SKIP_RQ_TESTS is True')
class TestFeedbackSetBatchDownloadApi(test.TestCase, TestHelper, TestCaseMixin):
    """
    Tests the API for FeedbackSet compression.
    """
    viewclass = BatchCompressionAPIFeedbackSetView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/devilry_compressed_archives/', ignore_errors=True)
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def __mock_cradmin_app(self):
        mock_app = mock.MagicMock()
        mock_app.reverse_appurl.return_value = ''
        return mock_app

    def test_get_404_without_content_object_id(self):
        with self.assertRaises(Http404):
            self.mock_getrequest()

    def test_post_404_without_content_object_id(self):
        with self.assertRaises(Http404):
            self.mock_postrequest()

    def test_get_status_no_files(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals('{"status": "no-files"}', mockresponse.response.content)

    def test_get_status_not_started_unprocessed(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testfeedbackset, status=BatchOperation.STATUS_UNPROCESSED)

        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals('{"status": "not-started"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_archive_meta_has_deleted_datetime(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Run the batch task which creates a CompressedArchiveMeta entry.
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset
        )

        # Set the deleted datetime of the compressed archive.
        compressed_archive = CompressedArchiveMeta.objects.first()
        compressed_archive.deleted_datetime = timezone.now()
        compressed_archive.save()

        self._mock_batchoperation_status(context_object_id=testfeedbackset.id, status=BatchOperation.STATUS_FINISHED)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_new_file_is_added(self):
        # Tests that status not-created is returned when another file is added to the feedbackset.
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        commentuser = mommy.make(settings.AUTH_USER_MODEL)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset, user_role='student', user=commentuser)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset
        )
        self._mock_batchoperation_status(context_object_id=testfeedbackset.id, status=BatchOperation.STATUS_FINISHED)

        # Add a new file after a CompressedArchiveEntry is added.
        testcomment_added_after = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset, user_role='student', user=commentuser)
        commentfile_added_after = mommy.make('devilry_comment.CommentFile',
                                             comment=testcomment_added_after,
                                             filename='testfile.txt')
        commentfile_added_after.file.save('testfile.txt', ContentFile('testcontent'))
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_status_not_created_when_examiner_history_with_datetime_greater_than_last_compressed_archive(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testfeedbackset,
                   created_datetime=timezone.now() - timezone.timedelta(hours=1))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('core.ExaminerAssignmentGroupHistory',
                   assignment_group=testgroup,
                   user=mommy.make(settings.AUTH_USER_MODEL),
                   created_datetime=timezone.now())
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_status_not_created_when_candidate_history_with_datetime_greater_than_last_compressed_archive(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_datetime=timezone.now() - timezone.timedelta(hours=1))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('core.CandidateAssignmentGroupHistory',
                   assignment_group=testgroup,
                   user=mommy.make(settings.AUTH_USER_MODEL),
                   created_datetime=timezone.now())
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_status_not_created_when_new_feedbackset_is_created_after_last_compressed_archive(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        # testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1)
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testfeedbackset,
                   created_datetime=timezone.now())
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Create new feedbackset.
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(group=testgroup)

        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_status_not_created_when_feedbackset_deadline_is_moved(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testfeedbackset,
                   created_datetime=timezone.now())
        mommy.make('devilry_group.FeedbackSetDeadlineHistory', feedback_set=testfeedbackset)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_status_running(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testfeedbackset, status=BatchOperation.STATUS_RUNNING)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "running"}')

    def test_get_status_finished_with_compressed_archive_meta(self):
        # When the task is complete, it creates a CompressedArchiveMeta entry in
        # the database. This is simulated by NOT creating a BatchOperation, but just creating a CompressedArchive
        # instead. This is the first thing that gets checked in API.
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testfeedbackset)
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_getrequest(
            cradmin_app=mock_cradmin_app,
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content,
                          '{"status": "finished", "download_link": "url-to-downloadview"}')

    def test_post_marks_archive_as_deleted_if_new_files_are_added(self):
        # Tests that post marks archive as deleted if new files are added
        # and there exists a CompressedArchiveMeta for the FeedbackSet.
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        compressed_archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                                             content_object=testfeedbackset)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self.mock_postrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertIsNotNone(CompressedArchiveMeta.objects.get(id=compressed_archive_meta.id).deleted_datetime)

    def test_post_batchoperation_not_started(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testfeedbackset, status=BatchOperation.STATUS_UNPROCESSED)
        mockresponse = self.mock_postrequest(
            cradmin_app=self.__mock_cradmin_app(),
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals({'status': 'not-started'}, json.loads(mockresponse.response.content))

    def test_post_status_finished_when_compressed_archive_exists(self):
        # Tests that post returns status finished with download-link if
        # CompressedArchiveMeta exists with deleted_datetime as None.
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testfeedbackset)

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_postrequest(
            cradmin_app=mock_cradmin_app,
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
                          json.loads(mockresponse.response.content))

        # mock return value for reverse_appurl
        with self.assertNumQueries(10):
            mockresponse = self.mock_postrequest(
                cradmin_app=mock_cradmin_app,
                viewkwargs={
                    'content_object_id': testfeedbackset.id
                })
        self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
                          json.loads(mockresponse.response.content))
