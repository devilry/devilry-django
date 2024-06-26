# Python imports
import os
import shutil
from zipfile import ZipFile

# Third party imports
from model_bakery import baker
from ievv_opensource.ievv_batchframework import batchregistry

# Django imports
from django.conf import settings
from django.test import TestCase, override_settings
from django.core.files.base import ContentFile
from django.utils import timezone

# Devilry imports
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import tasks
from devilry.devilry_group import devilry_group_baker_factories as group_baker
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


@override_settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY='devilry_compressed_archives')
class TestFeedbackSetBatchTask(TestCompressed):
    def __make_comment_file(self, feedback_set, file_name, file_content, user_role='student', **comment_kwargs):
        comment = baker.make(
            'devilry_group.GroupComment',
            feedback_set=feedback_set,
            user_role=user_role, **comment_kwargs)
        comment_file = baker.make(
            'devilry_comment.CommentFile', comment=comment,
            filename=file_name)
        comment_file.file.save(file_name, ContentFile(file_content))
        return comment_file

    def test_batchframework_no_files(self):
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished()
        baker.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user_role='student',
            user__shortname='testuser@example.com')

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)
        self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

    def test_batchframework(self):
        # Tests that the archive has been created.
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished()
        testcomment = baker.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user_role='student',
            user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(
            content_object_id=testfeedbackset.id)
        self.assertIsNotNone(archive_meta)
        self.assertTrue(archive_meta.get_archive_backend().archive_exists())

    def test_batchframework_delete_meta(self):
        # Tests that the metaclass deletes the actual archive.
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished()
        testcomment = baker.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user_role='student',
            user__shortname='testuser@example.com')
        commentfile = baker.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
        archive_meta_id = archive_meta.id
        self.assertIsNotNone(archive_meta)
        self.assertTrue(archive_meta.get_archive_backend().archive_exists())

        # after delete
        archive_meta.delete()
        with self.assertRaises(archivemodels.CompressedArchiveMeta.DoesNotExist):
            archivemodels.CompressedArchiveMeta.objects.get(id=archive_meta_id)
        self.assertFalse(archive_meta.get_archive_backend().archive_exists())

    def test_batchframework_feedbackset_student_after_deadline(self):
        # Tests that files added after the deadline returned from FeedbackSet.get_current_deadline() is added under
        # 'uploaded_after_deadline'.
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1)
        )
        studentuser = baker.make(settings.AUTH_USER_MODEL, shortname='april')
        baker.make(
            'core.Candidate', assignment_group=testfeedbackset.group,
            relatedstudent__user=studentuser)
        self.__make_comment_file(
            feedback_set=testfeedbackset, file_name='testfile.txt',
            file_content='testcontent', user=studentuser)

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
        zipfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(
            zipfileobject.extractfile('after_deadline_not_part_of_delivery/testfile.txt').read(),
            b'testcontent')

    def test_batchframework_examiner_files_not_uploaded(self):
        # Tests that the file is added under 'uploaded_by_examiner'.
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished()
        self.__make_comment_file(
            feedback_set=testfeedbackset, file_name='testfile.txt',
            file_content='testcontent', user_role='examiner')

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)
        self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

    def test_batchframework_files_from_examiner_and_student(self):
        # Tests that the file uploaded by examiner is added to 'uploaded_by_examiner' subfolder,
        # and that file from student is added under 'delivery'.
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group__parentnode=testassignment)
        self.__make_comment_file(
            feedback_set=testfeedbackset, file_name='testfile_examiner.txt',
            file_content='examiner testcontent', user_role='examiner')
        self.__make_comment_file(
            feedback_set=testfeedbackset, file_name='testfile_student.txt',
            file_content='student testcontent', user_role='student')

        # Run batch operation
        self._run_actiongroup(
            name='batchframework_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset,
            started_by=None)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testfeedbackset.id)
        zipfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(1, len(zipfileobject.getnames()))
        self.assertEqual(zipfileobject.extractfile('testfile_student.txt').read(), b'student testcontent')
