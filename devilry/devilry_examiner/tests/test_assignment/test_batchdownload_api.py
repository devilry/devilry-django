import json
import shutil

import mock
from django import test
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
from devilry.devilry_examiner import tasks
from devilry.devilry_examiner.views.assignment.download_files.batch_download_api import \
    BatchCompressionAPIAssignmentView


class TestHelper(object):
    """
    Testhelper class for tests.
    """
    def _mock_batchoperation_status(self, context_object_id, status=BatchOperation.STATUS_UNPROCESSED):
        # helper function
        # Set the BatchOperation.status to the desired status for testing.
        # Defaults to unprocessed.
        batchoperation = BatchOperation.objects.get(context_object_id=context_object_id)
        batchoperation.operationtype = BatchCompressionAPIAssignmentView.batchoperation_type
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


class TestAssignmentBatchDownloadApi(test.TestCase, TestHelper, TestCaseMixin):
    viewclass = BatchCompressionAPIAssignmentView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/devilry_compressed_archives/', ignore_errors=True)
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def test_get_404_without_content_object_id(self):
        with self.assertRaises(Http404):
            self.mock_getrequest()

    def test_post_404_without_content_object_id(self):
        with self.assertRaises(Http404):
            self.mock_postrequest()

    def test_get_status_no_files(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testgroup.parentnode.id
            }
        )
        self.assertEquals('{"status": "no-files"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_started_unprocessed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id)
        mockresponse = self.mock_getrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals('{"status": "not-started"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_archive_meta_has_deleted_datetime(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testassignment,
                   deleted_datetime=timezone.now())
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id, status=BatchOperation.STATUS_FINISHED)
        mockresponse = self.mock_getrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals('{"status": "not-created"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_new_file_is_added(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id, status=BatchOperation.STATUS_FINISHED)
        mockresponse = self.mock_getrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_new_file_is_added_to_one_of_the_groups(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # Same relatedexaminer for both groups
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testexaminer_group1 = mommy.make('core.Examiner',
                                         assignmentgroup=testgroup1,
                                         relatedexaminer=relatedexaminer)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        testfeedbackset_group1 = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        testcomment1 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=testfeedbackset_group1,
                                  user_role='student',
                                  user__shortname='testuser1@example.com')
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
        commentfile1.file.save('testfile.txt', ContentFile('testcontent'))
        # Register archive with and add new file to testgroup 2
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment)
        testcomment2 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=testfeedbackset_group2,
                                  user_role='student',
                                  user__shortname='testuser2@example.com')
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile.txt')
        commentfile2.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id, status=BatchOperation.STATUS_FINISHED)
        mockresponse = self.mock_getrequest(
            requestuser=relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_running(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id, status=BatchOperation.STATUS_RUNNING)
        mockresponse = self.mock_getrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "running"}')

    def test_get_status_finished_with_link_to_downloadurl(self):
        # When the BatchOperation task is complete, it creates a CompressedArchiveMeta entry in
        # the database. This is simulated by NOT creating a BatchOperation, but just creating a CompressedArchive
        # instead. This is the first thing that gets checked in API.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment)
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_getrequest(
            cradmin_app=mock_cradmin_app,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals(mockresponse.response.content,
                          '{"status": "finished", "download_link": "url-to-downloadview"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_post_marks_archive_as_deleted_if_new_files_are_added(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        compressed_archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                                             content_object=testassignment)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self.mock_postrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            }
        )
        self.assertIsNotNone(CompressedArchiveMeta.objects.get(id=compressed_archive_meta.id).deleted_datetime)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_post_batchoperation_not_started(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id)
        mockresponse = self.mock_postrequest(
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals('{"status": "not-started"}', mockresponse.response.content)

    def test_post_status_finished_when_compressed_archive_exists(self):
        # Tests that post returns status finished with download-link if
        # CompressedArchiveMeta exists with deleted_datetime as None.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment)

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_postrequest(
            cradmin_app=mock_cradmin_app,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
                          json.loads(mockresponse.response.content))

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        with self.assertNumQueries(4):
            mockresponse = self.mock_postrequest(
                cradmin_app=mock_cradmin_app,
                requestuser=testexaminer.relatedexaminer.user,
                viewkwargs={
                    'content_object_id': testassignment.id
                })
        self.assertEquals('{"status": "finished", "download_link": "url-to-downloadview"}',
                          mockresponse.response.content)
