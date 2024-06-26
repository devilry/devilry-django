# -*- coding: utf-8 -*-


# Python imports
import os
import shutil
from zipfile import ZipFile

# Third party imports
from ievv_opensource.ievv_batchframework.batchregistry import ActionGroupSynchronousExecutionError
from model_bakery import baker
from ievv_opensource.ievv_batchframework import batchregistry

# Django imports
from django.conf import settings
from django.test import TestCase, override_settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.template import defaultfilters

# Devilry imports
from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_admin import tasks
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


class TestAssignmentCompressActionAssignmentGroupPermissions(TestCase):
    def test_user_is_superuser(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertIn(testgroup, group_queryset)

    def test_user_is_subjectadmin(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.parentnode.parentnode,
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertIn(testgroup, group_queryset)

    def test_user_is_subjectadmin_on_different_subject(self):
        other_subject = baker.make('core.Subject')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=other_subject,
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertNotIn(testgroup, group_queryset)

    def test_user_is_periodadmin(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertIn(testgroup, group_queryset)

    def test_user_is_periodadmin_on_different_period(self):
        other_period = baker.make('core.Period')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=other_period,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertNotIn(testgroup, group_queryset)

    def test_user_is_periodadmin_assignment_fully_anonymous(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertNotIn(testgroup, group_queryset)

    def test_user_is_periodadmin_assignment_semi_anonymous(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        group_queryset = tasks.AssignmentCompressAction()\
            .get_assignment_group_queryset(assignment=testassignment, user=testuser)
        self.assertNotIn(testgroup, group_queryset)


@override_settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY='devilry_compressed_archives')
class TestAssignmentBatchTask(TestCompressed):

    def __make_comment_file(self, feedback_set, file_name, file_content, **comment_kwargs):
        comment = baker.make(
            'devilry_group.GroupComment',
            feedback_set=feedback_set,
            user_role='student', **comment_kwargs)
        comment_file = baker.make(
            'devilry_comment.CommentFile', comment=comment,
            filename=file_name)
        comment_file.file.save(file_name, ContentFile(file_content))
        return comment_file

    def __make_simple_setup(self, assignment):
        """
        Shortcut for making a simple group with a student, feedback set and a comment file.
        """
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=group)
        self.__make_comment_file(
            feedback_set=feedbackset, file_name='testfile.txt',
            file_content='testcontent')
        baker.make('core.Candidate', assignment_group=group, relatedstudent__user__shortname='april')
        return feedbackset

    def test_superuser_has_access(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))

        # Superuser
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)

        self.__make_simple_setup(assignment=testassignment)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(1, len(tarfileobject.getnames()))
        self.assertTrue(tarfileobject.getnames()[0].startswith('{}'.format('april')))

    def test_subject_department_admin_has_access(self):
        subject = baker.make('core.Subject')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1),
            parentnode__parentnode=subject)

        # Subject admin
        subjectpermissiongroup = baker.make(
            'devilry_account.SubjectPermissionGroup', subject=subject,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(1, len(tarfileobject.getnames()))
        self.assertTrue(tarfileobject.getnames()[0].startswith('{}'.format('april')))

    def test_subject_department_admin_on_different_subject_does_not_have_access(self):
        other_subject = baker.make('core.Subject')
        subject = baker.make('core.Subject')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1),
            parentnode__parentnode=subject)

        # Subject admin
        subjectpermissiongroup = baker.make(
            'devilry_account.SubjectPermissionGroup', subject=other_subject,
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        with self.assertRaises(ActionGroupSynchronousExecutionError):
            self._run_actiongroup(
                name='batchframework_assignment',
                task=tasks.AssignmentCompressAction,
                context_object=testassignment,
                started_by=testuser)
            self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

    def test_subjectadmin_has_access(self):
        subject = baker.make('core.Subject')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1),
            parentnode__parentnode=subject)

        # Subject admin
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup', subject=subject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(1, len(tarfileobject.getnames()))
        self.assertTrue(tarfileobject.getnames()[0].startswith('{}'.format('april')))

    def test_subjectadmin_on_different_subject_does_not_have_access(self):
        other_subject = baker.make('core.Subject')
        subject = baker.make('core.Subject')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1),
            parentnode__parentnode=subject)

        # Subject admin
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=other_subject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        with self.assertRaises(ActionGroupSynchronousExecutionError):
            self._run_actiongroup(name='batchframework_assignment',
                                  task=tasks.AssignmentCompressAction,
                                  context_object=testassignment,
                                  started_by=testuser)
            self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

    def test_periodadmin_has_access(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.period)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser',
            user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        self.assertEqual(1, len(tarfileobject.getnames()))
        self.assertTrue(tarfileobject.getnames()[0].startswith('{}'.format('april')))

    def test_periodadmin_on_different_period_does_not_have_access(self):
        period = baker.make_recipe('devilry.apps.core.period_active')
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))

        # Period admin
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=period)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        self.__make_simple_setup(assignment=testassignment)

        with self.assertRaises(ActionGroupSynchronousExecutionError):
            self._run_actiongroup(
                name='batchframework_assignment',
                task=tasks.AssignmentCompressAction,
                context_object=testassignment,
                started_by=testuser)
            self.assertEqual(archivemodels.CompressedArchiveMeta.objects.count(), 0)

    def test_period_admin_one_group_before_deadline(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        testfeedbackset = self.__make_simple_setup(assignment=testassignment)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        path_to_file = os.path.join(
            'april',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
            'testfile.txt')
        self.assertEqual('testcontent', tarfileobject.extractfile(path_to_file).read().decode())

    def test_period_admin_one_group_after_deadline(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now())
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Add feedbackset with commentfile.
        testfeedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup)
        self.__make_comment_file(
            feedback_set=testfeedbackset, file_name='testfile.txt',
            file_content='testcontent')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user__shortname='april')

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        # Path inside the zipfile generated by the task.
        path_to_file = os.path.join(
            'april',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset.deadline_datetime, 'b.j.Y-H:i')),
            'after_deadline_not_part_of_delivery',
            'testfile.txt')
        self.assertEqual('testcontent', tarfileobject.extractfile(path_to_file).read().decode())

    def test_period_admin_three_groups_before_deadline(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(days=1))
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Create feedbackset for testgroup1 with commentfiles
        testfeedbackset_group1 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup1)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group1, file_name='testfile.txt',
            file_content='testcontent group 1')
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

        # Create feedbackset for testgroup2 with commentfiles
        testfeedbackset_group2 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup2)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group2, file_name='testfile.txt',
            file_content='testcontent group 2')
        baker.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

        # Create feedbackset for testgroup3 with commentfiles
        testfeedbackset_group3 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup3)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group3, file_name='testfile.txt',
            file_content='testcontent group 3')
        baker.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user__shortname='huey')

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = archive_meta.get_archive_backend().read_archive()
        path_to_file_group1 = os.path.join(
            'april',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group1.deadline_datetime, 'b.j.Y-H:i')),
            'testfile.txt')
        path_to_file_group2 = os.path.join(
            'dewey',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group2.deadline_datetime, 'b.j.Y-H:i')),
            'testfile.txt')
        path_to_file_group3 = os.path.join(
            'huey',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group3.deadline_datetime, 'b.j.Y-H:i')),
            'testfile.txt')
        self.assertEqual('testcontent group 1', tarfileobject.extractfile(path_to_file_group1).read().decode())
        self.assertEqual('testcontent group 2', tarfileobject.extractfile(path_to_file_group2).read().decode())
        self.assertEqual('testcontent group 3', tarfileobject.extractfile(path_to_file_group3).read().decode())

    def test_period_admin_three_groups_after_deadline(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() - timezone.timedelta(hours=1))
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Create feedbackset for testgroup1 with commentfiles
        testfeedbackset_group1 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup1)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group1, file_name='testfile.txt',
            file_content='testcontent group 1')
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user__shortname='april')

        # Create feedbackset for testgroup2 with commentfiles
        testfeedbackset_group2 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup2)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group2, file_name='testfile.txt',
            file_content='testcontent group 2')
        baker.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user__shortname='dewey')

        # Create feedbackset for testgroup3 with commentfiles
        testfeedbackset_group3 = group_baker.feedbackset_first_attempt_unpublished(group=testgroup3)
        self.__make_comment_file(
            feedback_set=testfeedbackset_group3, file_name='testfile.txt',
            file_content='testcontent group 3')
        baker.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user__shortname='huey')

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = tarfileobject = archive_meta.get_archive_backend().read_archive()
        path_to_file_group1 = os.path.join(
            'april',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group1.deadline_datetime, 'b.j.Y-H:i')),
            'after_deadline_not_part_of_delivery',
            'testfile.txt')
        path_to_file_group2 = os.path.join(
            'dewey',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group2.deadline_datetime, 'b.j.Y-H:i')),
            'after_deadline_not_part_of_delivery',
            'testfile.txt')
        path_to_file_group3 = os.path.join(
            'huey',
            'deadline-{}'.format(defaultfilters.date(
                testfeedbackset_group3.deadline_datetime, 'b.j.Y-H:i')),
            'after_deadline_not_part_of_delivery',
            'testfile.txt')
        self.assertEqual('testcontent group 1', tarfileobject.extractfile(path_to_file_group1).read().decode())
        self.assertEqual('testcontent group 2', tarfileobject.extractfile(path_to_file_group2).read().decode())
        self.assertEqual('testcontent group 3', tarfileobject.extractfile(path_to_file_group3).read().decode())

    def test_period_admin_duplicates(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(hours=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Create feedbackset for testgroup1 with commentfiles
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        comment_file_first = self.__make_comment_file(
            feedback_set=testfeedbackset,
            file_name='testfile.txt',
            file_content='first upload')
        self.__make_comment_file(
            feedback_set=testfeedbackset,
            file_name='testfile.txt',
            file_content='last upload')

        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='april')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = tarfileobject = archive_meta.get_archive_backend().read_archive()

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
        self.assertEqual('last upload', tarfileobject.extractfile(path_to_last_file).read().decode())
        self.assertEqual('first upload', tarfileobject.extractfile(path_to_old_duplicate_file).read().decode())

    def test_period_admin_duplicates_from_different_students(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=timezone.now() + timezone.timedelta(hours=1))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Create students
        student_user_april = baker.make(settings.AUTH_USER_MODEL, shortname='april')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user_april)
        student_user_dewey = baker.make(settings.AUTH_USER_MODEL, shortname='dewey')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user_dewey)

        # Create feedbackset for testgroup1 with commentfiles
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        comment_file_april = self.__make_comment_file(
            feedback_set=testfeedbackset,
            file_name='testfile.txt',
            file_content='by april',
            user=student_user_april)
        self.__make_comment_file(
            feedback_set=testfeedbackset,
            file_name='testfile.txt',
            file_content='by dewey',
            user=student_user_dewey)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = tarfileobject = archive_meta.get_archive_backend().read_archive()

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
        self.assertEqual('by dewey', tarfileobject.extractfile(path_to_last_file).read().decode())
        self.assertEqual('by april', tarfileobject.extractfile(path_to_old_duplicate_file).read().decode())

    def test_period_admin_duplicates_before_and_after_deadline(self):
        first_deadline = timezone.now() + timezone.timedelta(hours=1)
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='learn-python-basics',
            first_deadline=first_deadline)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Period admin
        periodpermissiongroup = baker.make(
            'devilry_account.PeriodPermissionGroup',
            period=testassignment.parentnode)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            'devilry_account.PermissionGroupUser', user=testuser,
            permissiongroup=periodpermissiongroup.permissiongroup)

        # Create feedbackset for testgroup with commentfiles
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        comment_file_first_upload = self.__make_comment_file(
            feedback_set=testfeedbackset,
            file_name='testfile.txt',
            file_content='first upload')
        self.__make_comment_file(
            feedback_set=testfeedbackset,
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

        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='april')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=student_user)

        # run actiongroup
        self._run_actiongroup(
            name='batchframework_assignment',
            task=tasks.AssignmentCompressAction,
            context_object=testassignment,
            started_by=testuser)

        archive_meta = archivemodels.CompressedArchiveMeta.objects.get(content_object_id=testassignment.id)
        tarfileobject = tarfileobject = archive_meta.get_archive_backend().read_archive()

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
        self.assertEqual('last upload', tarfileobject.extractfile(path_to_last_file).read().decode())
        self.assertEqual('first upload', tarfileobject.extractfile(path_to_old_duplicate_file).read().decode())
        self.assertEqual('last upload after deadline', tarfileobject.extractfile(path_to_last_file_after_deadline).read().decode())
        self.assertEqual('first upload after deadline', tarfileobject.extractfile(path_to_old_duplicate_file_after_deadline).read().decode())
