# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
from django.template import defaultfilters

# Devilry imports
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_examiner import tasks
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


class TestAssignmentCompressActionAssignmentGroupPermissions(TestCase):
    def test_examiner_has_access_to_all_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           short_name='learn-python-basics',
                                           first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup2)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup3)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup4)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertIn(testgroup1, group_queryset)
        self.assertIn(testgroup2, group_queryset)
        self.assertIn(testgroup3, group_queryset)
        self.assertIn(testgroup4, group_queryset)

    def test_examiner_has_access_to_some_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           short_name='learn-python-basics',
                                           first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup2)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertIn(testgroup1, group_queryset)
        self.assertIn(testgroup2, group_queryset)
        self.assertNotIn(testgroup3, group_queryset)
        self.assertNotIn(testgroup4, group_queryset)

    def test_examiner_does_not_have_access_to_groups_in_other_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment1 = mommy.make('core.Assignment', parentnode=period,
                                     first_deadline=timezone.now() + timezone.timedelta(days=1))
        testassignment2 = mommy.make('core.Assignment', parentnode=period,
                                     first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment1.parentnode)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup1)
        mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup2)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment1, user=testuser)
        self.assertIn(testgroup1, group_queryset)
        self.assertIn(testgroup2, group_queryset)
        self.assertNotIn(testgroup3, group_queryset)
        self.assertNotIn(testgroup4, group_queryset)


class TestAssignmentBatchTask(TestCompressed):

    def __make_comment_file(self, feedback_set, file_name, file_content, **comment_kwargs):
        comment = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedback_set,
                                  user_role='student', **comment_kwargs)
        comment_file = mommy.make('devilry_comment.CommentFile', comment=comment,
                                  filename=file_name)
        comment_file.file.save(file_name, ContentFile(file_content))
        return comment_file

    def test_no_comment_files(self):
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
            mommy.make('devilry_group.GroupComment',
                       feedback_set=testfeedbackset1,
                       user_role='student')
            mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

            # Add feedbackset with commentfile to the group the examiner does not have access to.
            testfeedbackset2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            mommy.make('devilry_group.GroupComment',
                       feedback_set=testfeedbackset2,
                       user_role='student')
            mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

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
            self.__make_comment_file(feedback_set=testfeedbackset1, file_name='testfile.txt',
                                     file_content='testcontent')
            mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

            # Add feedbackset with commentfile to the group the examiner does not have access to.
            testfeedbackset2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            self.__make_comment_file(feedback_set=testfeedbackset2, file_name='testfile.txt',
                                     file_content='testcontent')
            mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            self.assertEquals(1, len(zipfileobject.namelist()))
            self.assertTrue(zipfileobject.namelist()[0].startswith('{}'.format('april')))
            self.assertFalse(zipfileobject.namelist()[0].startswith('{}'.format('dewey')))

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
            self.__make_comment_file(feedback_set=testfeedbackset, file_name='testfile.txt',
                                     file_content='testcontent')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user__shortname='april')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            path_to_file = os.path.join('april',
                                        'deadline-{}'.format(defaultfilters.date(
                                            testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
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
            self.__make_comment_file(feedback_set=testfeedbackset, file_name='testfile.txt',
                                     file_content='testcontent')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user__shortname='april')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            # Path inside the zipfile generated by the task.
            path_to_file = os.path.join('april',
                                        'deadline-{}'.format(defaultfilters.date(
                                            testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                                        'after_deadline_not_part_of_delivery',
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
            self.__make_comment_file(feedback_set=testfeedbackset_group1, file_name='testfile.txt',
                                     file_content='testcontent group 1')
            mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

            # Create feedbackset for testgroup2 with commentfiles
            testfeedbackset_group2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            self.__make_comment_file(feedback_set=testfeedbackset_group2, file_name='testfile.txt',
                                     file_content='testcontent group 2')
            mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

            # Create feedbackset for testgroup3 with commentfiles
            testfeedbackset_group3 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
            self.__make_comment_file(feedback_set=testfeedbackset_group3, file_name='testfile.txt',
                                     file_content='testcontent group 3')
            mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user__shortname='huey')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            path_to_file_group1 = os.path.join('april',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group1.deadline_datetime, 'b.j.Y-H:i')),
                                               'testfile.txt')
            path_to_file_group2 = os.path.join('dewey',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group2.deadline_datetime, 'b.j.Y-H:i')),
                                               'testfile.txt')
            path_to_file_group3 = os.path.join('huey',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group3.deadline_datetime, 'b.j.Y-H:i')),
                                               'testfile.txt')
            self.assertEquals('testcontent group 1', zipfileobject.read(path_to_file_group1))
            self.assertEquals('testcontent group 2', zipfileobject.read(path_to_file_group2))
            self.assertEquals('testcontent group 3', zipfileobject.read(path_to_file_group3))

    def test_three_groups_after_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() - timezone.timedelta(hours=1))
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
            self.__make_comment_file(feedback_set=testfeedbackset_group1, file_name='testfile.txt',
                                     file_content='testcontent group 1')
            mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

            # Create feedbackset for testgroup2 with commentfiles
            testfeedbackset_group2 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
            self.__make_comment_file(feedback_set=testfeedbackset_group2, file_name='testfile.txt',
                                     file_content='testcontent group 2')
            mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

            # Create feedbackset for testgroup3 with commentfiles
            testfeedbackset_group3 = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
            self.__make_comment_file(feedback_set=testfeedbackset_group3, file_name='testfile.txt',
                                     file_content='testcontent group 3')
            mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user__shortname='huey')

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)
            path_to_file_group1 = os.path.join('april',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group1.deadline_datetime, 'b.j.Y-H:i')),
                                               'after_deadline_not_part_of_delivery',
                                               'testfile.txt')
            path_to_file_group2 = os.path.join('dewey',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group2.deadline_datetime, 'b.j.Y-H:i')),
                                               'after_deadline_not_part_of_delivery',
                                               'testfile.txt')
            path_to_file_group3 = os.path.join('huey',
                                               'deadline-{}'.format(defaultfilters.date(
                                                   testfeedbackset_group3.deadline_datetime, 'b.j.Y-H:i')),
                                               'after_deadline_not_part_of_delivery',
                                               'testfile.txt')
            self.assertEquals('testcontent group 1', zipfileobject.read(path_to_file_group1))
            self.assertEquals('testcontent group 2', zipfileobject.read(path_to_file_group2))
            self.assertEquals('testcontent group 3', zipfileobject.read(path_to_file_group3))

    def test_duplicates(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() + timezone.timedelta(hours=1))
            testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup)

            # Create feedbackset for testgroup1 with commentfiles
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
            comment_file_first = self.__make_comment_file(feedback_set=testfeedbackset,
                                                          file_name='testfile.txt',
                                                          file_content='first upload')
            comment_file_last = self.__make_comment_file(feedback_set=testfeedbackset,
                                                         file_name='testfile.txt',
                                                         file_content='last upload')

            student_user = mommy.make(settings.AUTH_USER_MODEL, shortname='april')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user)

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)

            path_to_last_file = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'testfile.txt')
            path_to_old_duplicate_file = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'old_duplicates',
                comment_file_first.get_filename_as_unique_string())
            self.assertEqual('last upload', zipfileobject.read(path_to_last_file))
            self.assertEqual('first upload', zipfileobject.read(path_to_old_duplicate_file))

    def test_duplicates_from_different_students(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=timezone.now() + timezone.timedelta(hours=1))
            testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup)
            student_user_april = mommy.make(settings.AUTH_USER_MODEL, shortname='april')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user_april)
            student_user_dewey = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user_dewey)

            # Create feedbackset for testgroup1 with commentfiles
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
            comment_file_april = self.__make_comment_file(feedback_set=testfeedbackset,
                                                          file_name='testfile.txt',
                                                          file_content='by april',
                                                          user=student_user_april)
            comment_file_dewey = self.__make_comment_file(feedback_set=testfeedbackset,
                                                          file_name='testfile.txt',
                                                          file_content='by dewey',
                                                          user=student_user_dewey)

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)

            path_to_last_file = os.path.join(
                'april, dewey',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'testfile.txt')
            path_to_old_duplicate_file = os.path.join(
                'april, dewey',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'old_duplicates',
                comment_file_april.get_filename_as_unique_string())
            self.assertEqual('by dewey', zipfileobject.read(path_to_last_file))
            self.assertEqual('by april', zipfileobject.read(path_to_old_duplicate_file))

    def test_duplicates_before_and_after_deadline(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            first_deadline = timezone.now() + timezone.timedelta(hours=1)
            testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                               short_name='learn-python-basics',
                                               first_deadline=first_deadline)
            testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

            testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor')
            related_examiner = mommy.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode)
            mommy.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=testgroup)

            # Create feedbackset for testgroup with commentfiles
            testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
            comment_file_first_upload = self.__make_comment_file(feedback_set=testfeedbackset,
                                                                 file_name='testfile.txt',
                                                                 file_content='first upload')
            self.__make_comment_file(feedback_set=testfeedbackset,
                                     file_name='testfile.txt',
                                     file_content='last upload')
            comment_file_first_upload_after_deadline = self.__make_comment_file(
                feedback_set=testfeedbackset,
                file_name='testfile.txt',
                file_content='first upload after deadline',
                published_datetime=timezone.now() + timezone.timedelta(hours=2))
            self.__make_comment_file(
                feedback_set=testfeedbackset,
                file_name='testfile.txt',
                file_content='last upload after deadline',
                published_datetime=timezone.now() + timezone.timedelta(hours=2))

            student_user = mommy.make(settings.AUTH_USER_MODEL, shortname='april')
            mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user)

            # run actiongroup
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)

            archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
            zipfileobject = ZipFile(archive_meta.archive_path)

            path_to_last_file = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'testfile.txt')
            path_to_old_duplicate_file = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'old_duplicates',
                comment_file_first_upload.get_filename_as_unique_string())
            path_to_last_file_after_deadline = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'after_deadline_not_part_of_delivery',
                'testfile.txt')
            path_to_old_duplicate_file_after_deadline = os.path.join(
                'april',
                'deadline-{}'.format(defaultfilters.date(
                    testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
                'after_deadline_not_part_of_delivery',
                'old_duplicates',
                comment_file_first_upload_after_deadline.get_filename_as_unique_string())
            self.assertEqual('last upload', zipfileobject.read(path_to_last_file))
            self.assertEqual('first upload', zipfileobject.read(path_to_old_duplicate_file))
            self.assertEqual('last upload after deadline', zipfileobject.read(path_to_last_file_after_deadline))
            self.assertEqual('first upload after deadline', zipfileobject.read(path_to_old_duplicate_file_after_deadline))
