import json
import shutil
import unittest

import mock
from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404
from django.test import override_settings
from django.utils import timezone
from cradmin_legacy.cradmin_testhelpers import TestCaseMixin
from ievv_opensource.ievv_batchframework import batchregistry
from ievv_opensource.ievv_batchframework.models import BatchOperation
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup
from devilry.project.develop.testhelpers import skip_rq_tests
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_dbcache import customsql
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_examiner import tasks
from devilry.devilry_examiner.views.assignment.download_files.batch_download_api import \
    BatchCompressionAPIAssignmentView


class TestHelper(object):
    """
    Testhelper class for tests.
    """
    def _mock_batchoperation(self, context_object, status, user):
        """
        Create a batchoperation for the context object passed as argument.
        This way we can easlily set the batchoperation status without running the actual task since the
        api checks the batchoperation status to determine the response data.
        """
        batchoperation = BatchOperation(
            operationtype=BatchCompressionAPIAssignmentView.batchoperation_type,
            context_object=context_object,
            status=status,
            started_by=user)
        batchoperation.save()

    def _mock_batchoperation_status(self, context_object_id, status=BatchOperation.STATUS_UNPROCESSED):
        # helper function
        # Set the BatchOperation.status to the desired status for testing.
        # Defaults to unprocessed.
        batchoperation = BatchOperation.objects.get(context_object_id=context_object_id)
        batchoperation.operationtype = BatchCompressionAPIAssignmentView.batchoperation_type
        batchoperation.status = status
        batchoperation.save()

    def _register_and_run_actiongroup(self, actiongroup_name, task, context_object, user=None):
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
                 test='test',
                 started_by=user)


@unittest.skipIf(skip_rq_tests.should_skip_tests_that_require_rq_async(),
                 reason='Tests that require RQ to run async. Disabled if DEVILRY_SKIP_RQ_TESTS is True')
class TestAssignmentBatchDownloadApi(test.TestCase, TestHelper, TestCaseMixin):
    viewclass = BatchCompressionAPIAssignmentView

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
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testgroup.parentnode.id
            }
        )
        self.assertEqual(b'{"status": "no-files"}', mockresponse.response.content)

    def test_get_status_not_started_unprocessed(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testassignment,
                                  status=BatchOperation.STATUS_UNPROCESSED,
                                  user=testexaminer.relatedexaminer.user)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(b'{"status": "not-started"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_archive_meta_has_deleted_datetime(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testassignment,
                   deleted_datetime=timezone.now())
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_examiner_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment
        )
        self._mock_batchoperation_status(context_object_id=testassignment.id, status=BatchOperation.STATUS_FINISHED)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(b'{"status": "not-created"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_new_file_is_added(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user)
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_examiner_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            user=testexaminer.relatedexaminer.user
        )
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_not_created_user_has_compressed_archive_as_examiner_role_but_not_as_admin(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.parentnode,
                                           permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        baker.make('core.Examiner', relatedexaminer__period=testassignment.parentnode,
                   assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testuser, created_by_role=CompressedArchiveMeta.CREATED_BY_ROLE_ADMIN)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testuser,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_not_created_when_examiner_history_with_datetime_greater_than_last_compressed_archive(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user,
                   created_datetime=timezone.now() - timezone.timedelta(hours=1))
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('core.ExaminerAssignmentGroupHistory',
                   assignment_group=testgroup,
                   user=baker.make(settings.AUTH_USER_MODEL),
                   created_datetime=timezone.now())
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_not_created_when_candidate_history_with_datetime_greater_than_last_compressed_archive(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user,
                   created_datetime=timezone.now() - timezone.timedelta(hours=1))
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('core.CandidateAssignmentGroupHistory',
                   assignment_group=testgroup,
                   user=baker.make(settings.AUTH_USER_MODEL),
                   created_datetime=timezone.now())
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_not_created_when_new_feedbackset_is_created_after_last_compressed_archive(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1)
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user,
                   created_datetime=timezone.now())
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Create new feedbackset
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_not_created_when_feedbackset_deadline_is_moved(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user,
                   created_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSetDeadlineHistory', feedback_set=testfeedbackset)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_new_file_is_added_to_one_of_the_groups(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Same relatedexaminer for both groups
        relatedexaminer = baker.make('core.RelatedExaminer')
        testexaminer_group1 = baker.make('core.Examiner',
                                         assignmentgroup=testgroup1,
                                         relatedexaminer=relatedexaminer)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        testfeedbackset_group1 = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        testcomment1 = baker.make('devilry_group.GroupComment',
                                  feedback_set=testfeedbackset_group1,
                                  user_role='student',
                                  user__shortname='testuser1@example.com')
        commentfile1 = baker.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
        commentfile1.file.save('testfile.txt', ContentFile('testcontent'))

        # Register archive with and add new file to testgroup 2
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=relatedexaminer.user, created_by_role=CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)

        # Run actiongroup
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_examiner_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            user=relatedexaminer.user
        )

        testcomment2 = baker.make('devilry_group.GroupComment',
                                  feedback_set=testfeedbackset_group2,
                                  user_role='student',
                                  user__shortname='testuser2@example.com')
        commentfile2 = baker.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile.txt')
        commentfile2.file.save('testfile.txt', ContentFile('testcontent'))
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "not-created"}')

    def test_get_status_running(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testassignment,
                                  status=BatchOperation.STATUS_RUNNING,
                                  user=testexaminer.relatedexaminer.user)
        mockresponse = self.mock_getrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content, b'{"status": "running"}')

    def test_get_status_finished_with_link_to_downloadurl(self):
        # When the BatchOperation task is complete, it creates a CompressedArchiveMeta entry in
        # the database. This is simulated by NOT creating a BatchOperation, but just creating a CompressedArchive
        # instead. This is the first thing that gets checked in API.
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testassignment,
                   created_by=testexaminer.relatedexaminer.user,
                   created_by_role=CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_getrequest(
            cradmin_app=mock_cradmin_app,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(mockresponse.response.content,
                          b'{"status": "finished", "download_link": "url-to-downloadview"}')

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_post_marks_archive_as_deleted_if_new_files_are_added(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        compressed_archive_meta = baker.make('devilry_compressionutil.CompressedArchiveMeta',
                                             content_object=testassignment,
                                             created_by=testexaminer.relatedexaminer.user,
                                             created_by_role=CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self.mock_postrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            }
        )
        self.assertIsNotNone(CompressedArchiveMeta.objects.get(id=compressed_archive_meta.id).deleted_datetime)

    def test_post_batchoperation_not_started(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._mock_batchoperation(context_object=testassignment,
                                  status=BatchOperation.STATUS_UNPROCESSED,
                                  user=testexaminer.relatedexaminer.user)
        mockresponse = self.mock_postrequest(
            cradmin_app=self.__mock_cradmin_app(),
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(b'{"status": "not-started"}', mockresponse.response.content)

    def test_post_compressed_archive_is_saved_as_examiner(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        relatedexaminer = baker.make('core.RelatedExaminer')
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer)
        testfeedbackset_group = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment1 = baker.make('devilry_group.GroupComment',
                                  feedback_set=testfeedbackset_group,
                                  user_role='student',
                                  user__shortname='testuser1@example.com')
        commentfile1 = baker.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
        commentfile1.file.save('testfile.txt', ContentFile('testcontent'))

        # Run actiongroup
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_examiner_compress_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            user=relatedexaminer.user
        )
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        self.mock_postrequest(
            cradmin_app=mock_cradmin_app,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual(CompressedArchiveMeta.objects.count(), 1)
        archive_meta = CompressedArchiveMeta.objects.get()
        self.assertEqual(archive_meta.created_by_role, CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)
        self.assertTrue(
            archive_meta.archive_path.startswith('devilry_testfiles/devilry_compressed_archives/examiner/'))

    def test_post_status_finished_when_compressed_archive_exists(self):
        # Tests that post returns status finished with download-link if
        # CompressedArchiveMeta exists with deleted_datetime as None.
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        baker.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testassignment, created_by=testexaminer.relatedexaminer.user,
                   created_by_role=CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_postrequest(
            cradmin_app=mock_cradmin_app,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={
                'content_object_id': testassignment.id
            })
        self.assertEqual({'status': 'finished', 'download_link': 'url-to-downloadview'},
                          json.loads(mockresponse.response.content))

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        with self.assertNumQueries(8):
            mockresponse = self.mock_postrequest(
                cradmin_app=mock_cradmin_app,
                requestuser=testexaminer.relatedexaminer.user,
                viewkwargs={
                    'content_object_id': testassignment.id
                })
        self.assertEqual(b'{"status": "finished", "download_link": "url-to-downloadview"}',
                          mockresponse.response.content)
