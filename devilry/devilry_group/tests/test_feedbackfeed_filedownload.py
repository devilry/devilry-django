
# Third party imports
from StringIO import StringIO
from zipfile import ZipFile
import mock
from model_mommy import mommy

# Django imports
from django.test import TestCase
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

# Devilry imports
from devilry.devilry_group.views import feedbackfeed_download_files
from devilry.devilry_group import models as group_models


class TestFileDownloadFeedbackfeedView(TestCase):
    """
    Test single file download
    """
    def test_single_file_download(self):
        # Test download of single file
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment', user=testuser, user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.FileDownloadFeedbackfeedView()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testcomment.feedback_set.group
        mockrequest.user = testuser
        response = testdownloader.get(mockrequest, testcomment.feedback_set.id, commentfile.id)
        self.assertEquals(response.content, 'testcontent')

    def test_file_download_user_not_in_group_403(self):
        # Test user can't download if not part of AssignmentGroup
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment', user_role='examiner')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.FileDownloadFeedbackfeedView()
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        response = testdownloader.get(mockrequest, testcomment.feedback_set.id, testcomment.id)
        self.assertEquals(403, response.status_code)

    def test_file_download_private_comment_403(self):
        # User can't download file if the comment it belongs to is private unless the user created it.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user_role='examiner',
                                 feedback_set__group=testgroup,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.FileDownloadFeedbackfeedView()
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        response = testdownloader.get(mockrequest, testcomment.feedback_set.id, testcomment.id)
        self.assertEquals(403, response.status_code)


class TestCompressedGroupCommentFileDownload(TestCase):
    """
    Test GroupComment files download
    """
    def test_groupcomment_files_download(self):
        # Test download of all files for GroupComment.
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment', user=testuser, user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedGroupCommentFileDownload()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testcomment.feedback_set.group
        mockrequest.user = testuser
        response = testdownloader.get(mockrequest, testcomment.id)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('testfile.txt')
        self.assertEquals(filecontents, 'testcontent')

    def test_groupcomment_download_user_not_in_group_403(self):
        # Test user can't download if not part of AssignmentGroup
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment', user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedGroupCommentFileDownload()
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        response = testdownloader.get(mockrequest, testcomment.id)
        self.assertEquals(403, response.status_code)

    def test_groupcomment_download_private_comment_403(self):
        # User cant download private comment unless the user created it.
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user_role='examiner',
                                 feedback_set__group=testgroup,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedGroupCommentFileDownload()
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        response = testdownloader.get(mockrequest, testcomment.id)
        self.assertEquals(403, response.status_code)


class TestCompressedFeedbackSetFileDownload(TestCase):
    """
    Test FeeedbackSet files download
    """
    def test_feedbackset_files_download(self):
        # Test download files from feedbackset
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                     deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        # Add student comment visible to everyone
        testcomment_student = mommy.make('devilry_group.GroupComment',
                                         feedback_set=testfeedbackset,
                                         user=testuser,
                                         user_role='student')
        commentfile_student = mommy.make('devilry_comment.CommentFile',
                                         comment=testcomment_student,
                                         filename='testfile-student.txt')
        commentfile_student.file.save('testfile.txt', ContentFile('student-testcontent'))

        # Add examiner comment visible to everyone
        testcomment_examiner = mommy.make('devilry_group.GroupComment',
                                          feedback_set=testfeedbackset,
                                          user_role='examiner')
        commentfile_examiner = mommy.make('devilry_comment.CommentFile',
                                          comment=testcomment_examiner,
                                          filename='testfile-examiner.txt')
        commentfile_examiner.file.save('testfile.txt', ContentFile('examiner-testcontent'))

        # Add examiner comment with private visibility
        testcomment_examiner_private = mommy.make('devilry_group.GroupComment',
                                                  visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                                  feedback_set=testfeedbackset,
                                                  user_role='examiner')
        commentfile_examiner_private = mommy.make('devilry_comment.CommentFile',
                                                  comment=testcomment_examiner_private,
                                                  filename='testfile-private-examiner.txt')
        commentfile_examiner_private.file.save('testfile.txt', ContentFile('examiner-private-testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedFeedbackSetFileDownloadView()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testfeedbackset.group
        mockrequest.user = testuser
        response = testdownloader.get(mockrequest, testcomment_student.feedback_set.id)
        zipfileobject = ZipFile(StringIO(response.content))
        self.assertEquals('student-testcontent', zipfileobject.read('uploaded_by_student/testfile-student.txt'))
        self.assertEquals('examiner-testcontent', zipfileobject.read('uploaded_by_examiner/testfile-examiner.txt'))
        with self.assertRaises(KeyError):
            self.assertEquals('examiner-private-testcontent',
                              zipfileobject.read('uploaded_by_examiner/testfile-private-examiner.txt'))

    def test_feedbackset_files_download_after_deadline(self):
        # Test download files from feedbackset
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                     deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        # Add student comment visible to everyone
        testcomment_student = mommy.make('devilry_group.GroupComment',
                                         feedback_set=testfeedbackset,
                                         user=testuser,
                                         user_role='student')
        commentfile_student = mommy.make('devilry_comment.CommentFile',
                                         comment=testcomment_student,
                                         filename='testfile-student.txt')
        commentfile_student.file.save('testfile.txt', ContentFile('student-testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedFeedbackSetFileDownloadView()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testfeedbackset.group
        mockrequest.user = testuser
        response = testdownloader.get(mockrequest, testcomment_student.feedback_set.id)
        zipfileobject = ZipFile(StringIO(response.content))
        self.assertEquals('student-testcontent', zipfileobject.read('uploaded_after_deadline/testfile-student.txt'))

    def test_feedbackset_download_user_not_in_group_403(self):
        # Test user can't download if not part of AssignmentGroup
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
        testcomment = mommy.make('devilry_group.GroupComment', user_role='student')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        testdownloader = feedbackfeed_download_files.CompressedFeedbackSetFileDownloadView()
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        response = testdownloader.get(mockrequest, testcomment.feedback_set.id)
        self.assertEquals(403, response.status_code)