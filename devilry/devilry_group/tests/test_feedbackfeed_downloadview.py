# Python imports
import os
import shutil
from StringIO import StringIO
from zipfile import ZipFile

# Django imports
from django.utils import timezone
from django.core.files.base import ContentFile
from django.test import TestCase
from django_cradmin import cradmin_testhelpers

# 3rd party imports
from ievv_opensource.ievv_batchframework import batchregistry
from model_mommy import mommy

# Devilry imports
from devilry.devilry_group import tasks
from devilry.devilry_group.views.download_files import feedbackfeed_downloadviews


class CompressionTestSetup(TestCase):
    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree(self.backend_path, ignore_errors=True)
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class GroupCommentArchiveDownload(CompressionTestSetup, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_downloadviews.WaitForDownload

    def test_archive_response_200(self):
        with self.settings(DEVILRY_ZIPFILE_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment',
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_groupcomment',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.GroupCommentCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(actiongroup_name='batchframework_groupcomment',
                                                      context_object=testcomment,
                                                      test='test')
            mockresponse = self.mock_getrequest(viewkwargs={'pk': testcomment.id})
            self.assertEquals(mockresponse.response.status_code, 200)

    def test_archive_response_archive(self):
        with self.settings(DEVILRY_ZIPFILE_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment',
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_groupcomment',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.GroupCommentCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(actiongroup_name='batchframework_groupcomment',
                                                      context_object=testcomment,
                                                      test='test')
            mockresponse = self.mock_getrequest(viewkwargs={'pk': testcomment.id})
            zipfile = ZipFile(StringIO(mockresponse.response.content))
            filecontents = zipfile.read('testfile.txt')
            self.assertEquals(mockresponse.response.status_code, 200)
            self.assertEquals(filecontents, 'testcontent')


class FeedbackSetArchiveDownload(CompressionTestSetup, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_downloadviews.WaitForDownload

    def test_archive_response_200(self):
        with self.settings(DEVILRY_ZIPFILE_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet', deadline_datetime=timezone.now())
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchdownload_feedbackset',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.FeedbackSetCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchdownload_feedbackset',
                    context_object=testfeedbackset,
                    test='test'
            )
            mockresponse = self.mock_getrequest(viewkwargs={'pk': testfeedbackset.id})
            self.assertEquals(mockresponse.response.status_code, 200)

    def test_archive_response_200_feedbackset_without_deadline(self):
        with self.settings(DEVILRY_ZIPFILE_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet')
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchdownload_feedbackset',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.FeedbackSetCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchdownload_feedbackset',
                    context_object=testfeedbackset,
                    test='test'
            )
            mockresponse = self.mock_getrequest(viewkwargs={'pk': testfeedbackset.id})
            self.assertEquals(mockresponse.response.status_code, 200)
