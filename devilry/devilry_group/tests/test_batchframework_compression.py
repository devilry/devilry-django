# Python imports
import os
import shutil

# Third party imports
from model_mommy import mommy
from ievv_opensource.ievv_batchframework import batchregistry

# Django imports
from django.test import TestCase
from django.core.files.base import ContentFile
from django.utils import timezone

# Devilry imports
from devilry.devilry_group import tasks
from devilry.devilry_compressionutil import models as archivemodels


class DummyAction(batchregistry.Action):
    def execute(self):
        return 'test'


class TestCompressed(TestCase):
    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree(self.backend_path, ignore_errors=True)


class TestCompressedGroupCommentFileDownload(TestCompressed):

    def test_batchframework(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
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

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))


class TestCompressedFeedbackSetFileDownload(TestCompressed):

    def test_batchframework(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                         deadline_datetime=timezone.now() + timezone.timedelta(days=1))
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_feedbackset',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.FeedbackSetCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchframework_feedbackset',
                    context_object=testfeedbackset,
                    test='test')

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))
