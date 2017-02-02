# Python imports
import shutil
import unittest

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404
from django.test import TestCase
from django_cradmin.cradmin_testhelpers import TestCaseMixin
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.download_files import batch_download_files


class AbstractTestCase(TestCase):
    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        self.backend_path = 'devilry_testfiles/devilry_compressed_archives/'

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree(self.backend_path, ignore_errors=True)
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class TestFileDownloadFeedbackfeedView(TestCase, TestCaseMixin):
    """
    Test single file download
    """
    viewclass = batch_download_files.FileDownloadFeedbackfeedView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_single_file_download(self):
        # Test download of single file
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testgroup.feedbackset_set.first(),
                                 user=testuser,
                                 user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mockresponse = self.mock_getrequest(
                requestuser=testuser,
                cradmin_role=testgroup,
                viewkwargs={
                    'commentfile_id': commentfile.id
                })
        self.assertEquals(mockresponse.response.content, 'testcontent')

    def test_single_file_download_two_users(self):
        # Test download of single file
        testgroup = mommy.make('core.AssignmentGroup')
        testuser1 = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL, shortname='april@example.com', fullname='April Duck')
        candidate1 = mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser1)
        candidate2 = mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser2)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testgroup.feedbackset_set.first(),
                                 user=testuser1,
                                 user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mockresponse1 = self.mock_getrequest(
                requestuser=candidate1.relatedstudent.user,
                cradmin_role=candidate1.assignment_group,
                viewkwargs={
                    'commentfile_id': commentfile.id
                })
        mockresponse2 = self.mock_getrequest(
                requestuser=candidate2.relatedstudent.user,
                cradmin_role=candidate2.assignment_group,
                viewkwargs={
                    'commentfile_id': commentfile.id
                })
        self.assertEquals(mockresponse1.response.content, 'testcontent')
        self.assertEquals(mockresponse2.response.content, 'testcontent')

    def test_file_download_user_not_in_group_404(self):
        # Test user can't download if not part of AssignmentGroup
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user_role='examiner',
                                 feedback_set=devilry_group_mommy_factories.make_first_feedbackset_in_group())
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        with self.assertRaises(Http404):
            self.mock_getrequest(
                requestuser=testuser,
                cradmin_role=testgroup,
                viewkwargs={
                    'commentfile_id': commentfile.id
                })

    def test_file_download_private_comment_404(self):
        # User can't download file if the comment it belongs to is private unless the user created it.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user_role='examiner',
                                 feedback_set=testgroup.feedbackset_set.first(),
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        with self.assertRaises(Http404):
            self.mock_getrequest(
                requestuser=testuser,
                cradmin_role=testgroup,
                viewkwargs={
                    'commentfile_id': commentfile.id
                })
