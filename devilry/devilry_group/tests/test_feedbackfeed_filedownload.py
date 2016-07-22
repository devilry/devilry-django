
# Third party imports
from StringIO import StringIO
from zipfile import ZipFile
import mock
from model_mommy import mommy

# Django imports
from django.test import TestCase
from django.conf import settings
from django.core.files.base import ContentFile

# Devilry imports
from devilry.devilry_group.views import feedbackfeed_download_files
from devilry.devilry_group import models as group_models


class TestFeedbackFeedFileDownload(TestCase):

    def test_single_file_download(self):
        pass

    def test_file_download_user_not_in_group_403(self):
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

    def test_groupcomment_download_user_not_in_group_403(self):
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

    def test_feedbackset_download_user_not_in_group_403(self):
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

    # def test_groupcomment_files_download(self):
    #     # Test download of all files for GroupComment.
    #     testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
    #     testcomment = mommy.make('devilry_group.GroupComment', user=testuser, user_role='student')
    #     commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
    #     commentfile.file.save('testfile.txt', ContentFile('testcontent'))
    #
    #     testdownloader = feedbackfeed_download_files.CompressedGroupCommentFileDownload()
    #     mockrequest = mock.MagicMock()
    #     response = testdownloader.get(mockrequest, testcomment.id)
    #     zipfileobject = ZipFile(StringIO(response.content))
    #     filecontents = zipfileobject.read('comment-student-dewey@example.com/testfile.txt')
    #     self.assertEquals(filecontents, 'testcontent')

    def test_feedbackset_files_download(self):
        pass
