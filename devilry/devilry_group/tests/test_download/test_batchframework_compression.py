# Python imports
import os
import shutil
from zipfile import ZipFile

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


class TestCompressed(TestCase):
    def setUp(self):
        # Sets up a directory where files can be added. Is removed by tearDown.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    # def tearDown(self):
    #     # Ignores errors if the path is not created.
    #     shutil.rmtree(self.backend_path, ignore_errors=True)
    #     shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class TestGroupCommentBatchTask(TestCompressed):

    def test_batchframework(self):
        # Tests that the archive has been created.
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

    def test_batchframework_file_uploaded_by_examiner(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment',
                                     user_role='examiner',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('examiner testcontent'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_groupcomment',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.GroupCommentCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchframework_groupcomment',
                    context_object=testcomment,
                    test='test')

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))
            zipfileobject = ZipFile(archive_meta.archive_path)
            filecontents = zipfileobject.read('testfile.txt')
            self.assertEquals(filecontents, 'examiner testcontent')

    def test_batchframework_examiner_multiple_files(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment',
                                     user_role='examiner',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile1.txt')
            commentfile.file.save('testfile1.txt', ContentFile('examiner testcontent1'))
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile2.txt')
            commentfile.file.save('testfile2.txt', ContentFile('examiner testcontent2'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_groupcomment',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.GroupCommentCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchframework_groupcomment',
                    context_object=testcomment,
                    test='test')

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('testfile1.txt'), 'examiner testcontent1')
            self.assertEquals(zipfileobject.read('testfile2.txt'), 'examiner testcontent2')

    def test_batchframework_student_multiple_files(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment',
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile1.txt')
            commentfile.file.save('testfile1.txt', ContentFile('student testcontent1'))
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile2.txt')
            commentfile.file.save('testfile2.txt', ContentFile('student testcontent2'))

            batchregistry.Registry.get_instance().add_actiongroup(
                batchregistry.ActionGroup(
                    name='batchframework_groupcomment',
                    mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                    actions=[
                        tasks.GroupCommentCompressAction
                    ]))
            batchregistry.Registry.get_instance().run(
                    actiongroup_name='batchframework_groupcomment',
                    context_object=testcomment,
                    test='test')

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_meta.archive_path))
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('testfile1.txt'), 'student testcontent1')
            self.assertEquals(zipfileobject.read('testfile2.txt'), 'student testcontent2')


class TestFeedbackSetBatchTask(TestCompressed):

    def test_batchframework(self):
        # Tests that the archive has been created.
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

    def test_batchframework_delete_meta(self):
        # Tests that the metaclass deletes the actual archive.
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
            archive_path = archive_meta.archive_path
            archive_meta_id = archive_meta.id
            self.assertIsNotNone(archive_meta)
            self.assertTrue(os.path.exists(archive_path))

            # after delete
            archive_meta.delete()
            with self.assertRaises(archivemodels.CompressedArchiveMeta.DoesNotExist):
                archivemodels.CompressedArchiveMeta.objects.get(id=archive_meta_id)
            self.assertFalse(os.path.exists(archive_path))

    def test_batchframework_feedbackset_student_without_deadline(self):
        # Tests that files added when the FeedbackSet has no deadline is added under 'delivery'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet')
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('student testcontent'))

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
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('delivery/testfile.txt'), 'student testcontent')

    def test_batchframework_feedbackset_student_after_deadline(self):
        # Tests that files added after the deadline returned from FeedbackSet.get_current_deadline() is added under
        # 'uploaded_after_deadline'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                         deadline_datetime=timezone.now() - timezone.timedelta(days=1))
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('student testcontent'))

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
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('uploaded_after_deadline/testfile.txt'), 'student testcontent')

    def test_batchframework_examiner_file_uploaded_by_examiner(self):
        # Tests that the file is added under 'uploaded_by_examiner'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet', deadline_datetime=timezone.now())
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='examiner',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('examiner testcontent'))

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
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('uploaded_by_examiner/testfile.txt'), 'examiner testcontent')

    def test_batchframework_files_from_examiner_and_student(self):
        # Tests that the file uploaded by examiner is added to 'uploaded_by_examiner' subfolder,
        # and that file from student is added under 'delivery'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testfeedbackset = mommy.make('devilry_group.FeedbackSet')
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
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(zipfileobject.read('delivery/testfile_student.txt'), 'student testcontent')
            self.assertEquals(zipfileobject.read('uploaded_by_examiner/testfile_examiner.txt'), 'examiner testcontent')
