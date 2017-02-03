# Python imports
import os
import shutil
from zipfile import ZipFile

# Third party imports
from model_mommy import mommy
from ievv_opensource.ievv_batchframework import batchregistry

# Django imports
from django.conf import settings
from django.test import TestCase
from django.core.files.base import ContentFile
from django.utils import timezone

# Devilry imports
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import tasks
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_compressionutil import models as archivemodels


class TestCompressed(TestCase):
    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        AssignmentGroupDbCacheCustomSql().initialize()
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree(self.backend_path, ignore_errors=True)
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def _run_actiongroup(self, name, task, context_object, started_by):
        """
        Helper method for adding operation and running task.

        Saves a little code in the test-function.
        """
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name=name,
                mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                actions=[
                    task
                ]))
        batchregistry.Registry.get_instance().run(
            actiongroup_name=name,
            context_object=context_object,
            started_by=started_by,
            test='test')


class TestFeedbackSetBatchTask(TestCompressed):

    def test_batchframework(self):
        # Tests that the archive has been created.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            # Run batch operation
            self._run_actiongroup(name='batchframework_feedbackset',
                                  task=tasks.FeedbackSetCompressAction,
                                  context_object=testfeedbackset,
                                  started_by=None)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))

    def test_batchframework_delete_meta(self):
        # Tests that the metaclass deletes the actual archive.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            # Run batch operation
            self._run_actiongroup(name='batchframework_feedbackset',
                                  task=tasks.FeedbackSetCompressAction,
                                  context_object=testfeedbackset,
                                  started_by=None)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            archive_path = archive_meta.archive_path
            archive_meta_id = archive_meta.id
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_path))

            # after delete
            archive_meta.delete()
            with self.assertRaises(archivemodels.CompressedArchiveMeta.DoesNotExist):
                archivemodels.CompressedArchiveMeta.objects.get(id=archive_meta_id)
            self.assertFalse(os.path.exists(archive_path))

    # def test_batchframework_feedbackset_student_without_deadline(self):
    #     # Tests that files added when the FeedbackSet has no deadline is added under 'delivery'.
    #     with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
    #         testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #         testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #         testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
    #         testcomment = mommy.make('devilry_group.GroupComment',
    #                                  feedback_set=testfeedbackset,
    #                                  user_role='student',
    #                                  user__shortname='testuser@example.com')
    #         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
    #         commentfile.file.save('testfile.txt', ContentFile('student testcontent'))
    #
    #         # Run batch operation
    #         self._run_actiongroup(name='batchframework_feedbackset',
    #                               task=tasks.FeedbackSetCompressAction,
    #                               context_object=testfeedbackset,
    #                               started_by=None)
    #
    #         archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
    #         zipfileobject = ZipFile(archive_meta.archive_path)
    #         self.assertEquals(zipfileobject.read('delivery/testfile.txt'), 'student testcontent')

    def test_batchframework_feedbackset_student_after_deadline(self):
        # Tests that files added after the deadline returned from FeedbackSet.get_current_deadline() is added under
        # 'uploaded_after_deadline'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1)
            )
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('student testcontent'))

            # Run batch operation
            self._run_actiongroup(name='batchframework_feedbackset',
                                  task=tasks.FeedbackSetCompressAction,
                                  context_object=testfeedbackset,
                                  started_by=None)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('uploaded_after_deadline/testfile.txt'), 'student testcontent')

    def test_batchframework_examiner_file_uploaded_by_examiner(self):
        # Tests that the file is added under 'uploaded_by_examiner'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='examiner',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('examiner testcontent'))

            # Run batch operation
            self._run_actiongroup(name='batchframework_feedbackset',
                                  task=tasks.FeedbackSetCompressAction,
                                  context_object=testfeedbackset,
                                  started_by=None)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('uploaded_by_examiners_and_admins/testfile.txt'),
                              'examiner testcontent')

    def test_batchframework_files_from_examiner_and_student(self):
        # Tests that the file uploaded by examiner is added to 'uploaded_by_examiner' subfolder,
        # and that file from student is added under 'delivery'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               first_deadline=timezone.now() + timezone.timedelta(days=1))
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=testassignment)

            # examiner-comment with file.
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='examiner',
                                     user__shortname='testexaminer@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment,
                                     filename='testfile_examiner.txt')
            commentfile.file.save('testfile_examiner.txt', ContentFile('examiner testcontent'))

            # student-comment with file
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='teststudent@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment,
                                     filename='testfile_student.txt')
            commentfile.file.save('testfile_student.txt', ContentFile('student testcontent'))

            # Run batch operation
            self._run_actiongroup(name='batchframework_feedbackset',
                                  task=tasks.FeedbackSetCompressAction,
                                  context_object=testfeedbackset,
                                  started_by=None)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('delivery/testfile_student.txt'), 'student testcontent')
            self.assertEquals(zipfileobject.read('uploaded_by_examiners_and_admins/testfile_examiner.txt'),
                              'examiner testcontent')
