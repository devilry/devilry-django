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
from devilry.apps.core.models import AssignmentGroup
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
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
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
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
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
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1)
            )
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
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
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
            self.assertEquals(zipfileobject.read('uploaded_by_examiners_and_admins/testfile.txt'),
                              'examiner testcontent')

    def test_batchframework_files_from_examiner_and_student(self):
        # Tests that the file uploaded by examiner is added to 'uploaded_by_examiner' subfolder,
        # and that file from student is added under 'delivery'.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            # testfeedbackset = mommy.make('devilry_group.FeedbackSet')
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()

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
            self.assertEquals(zipfileobject.read('uploaded_by_examiners_and_admins/testfile_examiner.txt'),
                              'examiner testcontent')


class TestAssignmentBatchTask(TestCompressed):

    def __run_actiongroup(self, context_object, started_by):
        """
        Helper method for adding operation and running task.

        Saves a little code in the test-function.
        """
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name='batchframework_assignment',
                mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                actions=[
                    tasks.AssignmentCompressAction
                ]))
        batchregistry.Registry.get_instance().run(
            actiongroup_name='batchframework_assignment',
            context_object=context_object,
            started_by=started_by,
            test='test')

    def test_only_groups_examiner_has_access_to(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() + timezone.timedelta(days=1))
            testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            # Create examiner.
            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)

            # Add feedbackset with commentfile to the group the examiner has access to.
            testfeedbackset1 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
            testcomment1 = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset1,
                                     user_role='student',
                                     user__shortname='testuser1@example.com')
            commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
            commentfile1.file.save('testfile.txt', ContentFile('testcontent'))

            # Add feedbackset with commentfile to the group the examiner does not have access to.
            testfeedbackset2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            testcomment2 = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset2,
                                     user_role='student',
                                     user__shortname='testuser2@example.com')
            commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile.txt')
            commentfile2.file.save('testfile.txt', ContentFile('testcontent'))

            # run actiongroup
            self.__run_actiongroup(context_object=testassignment, started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(1, len(zipfileobject.namelist()))
            self.assertTrue(zipfileobject.namelist()[0].startswith('group-{}'.format(testgroup1)))
            self.assertFalse(zipfileobject.namelist()[0].startswith('group-{}'.format(testgroup2)))

    def test_one_group_before_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() + timezone.timedelta(days=1))
            testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            # Create examiner.
            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup)

            # Add feedbackset with commentfile.
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            # run actiongroup
            self.__run_actiongroup(context_object=testassignment, started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            # Path inside the zipfile generated by the task.
            path_to_file = os.path.join('group-{}'.format(testgroup),
                                        'deadline{}'.format(testfeedbackset.current_deadline()),
                                        'delivery',
                                        'testfile.txt')
            self.assertEquals('testcontent', zipfileobject.read(path_to_file))

    def test_one_group_after_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now())
            testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            # Create examiner.
            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup)

            # Add feedbackset with commentfile.
            testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
            testcomment = mommy.make('devilry_group.GroupComment',
                                     feedback_set=testfeedbackset,
                                     user_role='student',
                                     user__shortname='testuser@example.com')
            commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
            commentfile.file.save('testfile.txt', ContentFile('testcontent'))

            # run actiongroup
            self.__run_actiongroup(context_object=testassignment, started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            # Path inside the zipfile generated by the task.
            path_to_file = os.path.join('group-{}'.format(testgroup),
                                        'deadline{}'.format(testfeedbackset.current_deadline()),
                                        'uploaded_after_deadline',
                                        'testfile.txt')
            self.assertEquals('testcontent', zipfileobject.read(path_to_file))

    def test_three_groups_before_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() + timezone.timedelta(days=1))
            testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            # Create user as examiner on all groups.
            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup2)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup3)

            # Create feedbackset for testgroup1 with commentfiles
            testfeedbackset_group1 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
            testcomment1 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group1,
                                      user_role='student',
                                      user__shortname='testuser1@example.com')
            commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
            commentfile1.file.save('testfile.txt', ContentFile('testcontent group 1'))

            # Create feedbackset for testgroup2 with commentfiles
            testfeedbackset_group2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            testcomment2 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group2,
                                      user_role='student',
                                      user__shortname='testuser2@example.com')
            commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile.txt')
            commentfile2.file.save('testfile.txt', ContentFile('testcontent group 2'))

            # Create feedbackset for testgroup3 with commentfiles
            testfeedbackset_group3 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
            testcomment3 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group3,
                                      user_role='student',
                                      user__shortname='testuser3@example.com')
            commentfile3 = mommy.make('devilry_comment.CommentFile', comment=testcomment3, filename='testfile.txt')
            commentfile3.file.save('testfile.txt', ContentFile('testcontent group 3'))

            # run actiongroup
            self.__run_actiongroup(context_object=testassignment, started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            path_to_file_group1 = os.path.join('group-{}'.format(testgroup1),
                                               'deadline{}'.format(testfeedbackset_group1.current_deadline()),
                                               'delivery',
                                               'testfile.txt')
            path_to_file_group2 = os.path.join('group-{}'.format(testgroup2),
                                               'deadline{}'.format(testfeedbackset_group2.current_deadline()),
                                               'delivery',
                                               'testfile.txt')
            path_to_file_group3 = os.path.join('group-{}'.format(testgroup3),
                                               'deadline{}'.format(testfeedbackset_group3.current_deadline()),
                                               'delivery',
                                               'testfile.txt')
            self.assertEquals('testcontent group 1', zipfileobject.read(path_to_file_group1))
            self.assertEquals('testcontent group 2', zipfileobject.read(path_to_file_group2))
            self.assertEquals('testcontent group 3', zipfileobject.read(path_to_file_group3))

    def test_three_groups_after_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now())
            testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            # Create user as examiner on all groups.
            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup2)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup3)

            # Create feedbackset for testgroup1 with commentfiles
            testfeedbackset_group1 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
            testcomment1 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group1,
                                      user_role='student',
                                      user__shortname='testuser1@example.com')
            commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile.txt')
            commentfile1.file.save('testfile.txt', ContentFile('testcontent group 1'))

            # Create feedbackset for testgroup2 with commentfiles
            testfeedbackset_group2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            testcomment2 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group2,
                                      user_role='student',
                                      user__shortname='testuser2@example.com')
            commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile.txt')
            commentfile2.file.save('testfile.txt', ContentFile('testcontent group 2'))

            # Create feedbackset for testgroup3 with commentfiles
            testfeedbackset_group3 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
            testcomment3 = mommy.make('devilry_group.GroupComment',
                                      feedback_set=testfeedbackset_group3,
                                      user_role='student',
                                      user__shortname='testuser3@example.com')
            commentfile3 = mommy.make('devilry_comment.CommentFile', comment=testcomment3, filename='testfile.txt')
            commentfile3.file.save('testfile.txt', ContentFile('testcontent group 3'))

            # run actiongroup
            self.__run_actiongroup(context_object=testassignment, started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            path_to_file_group1 = os.path.join('group-{}'.format(testgroup1),
                                               'deadline{}'.format(testfeedbackset_group1.current_deadline()),
                                               'uploaded_after_deadline',
                                               'testfile.txt')
            path_to_file_group2 = os.path.join('group-{}'.format(testgroup2),
                                               'deadline{}'.format(testfeedbackset_group2.current_deadline()),
                                               'uploaded_after_deadline',
                                               'testfile.txt')
            path_to_file_group3 = os.path.join('group-{}'.format(testgroup3),
                                               'deadline{}'.format(testfeedbackset_group3.current_deadline()),
                                               'uploaded_after_deadline',
                                               'testfile.txt')
            self.assertEquals('testcontent group 1', zipfileobject.read(path_to_file_group1))
            self.assertEquals('testcontent group 2', zipfileobject.read(path_to_file_group2))
            self.assertEquals('testcontent group 3', zipfileobject.read(path_to_file_group3))
