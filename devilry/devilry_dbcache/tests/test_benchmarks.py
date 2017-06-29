import unittest

from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group.models import FeedbackSet, GroupComment


class TimeExecution(object):
    def __init__(self, label):
        self.start_time = None
        self.label = label

    def __enter__(self):
        self.start_time = timezone.now()

    def __exit__(self, ttype, value, traceback):
        end_time = timezone.now()
        duration = (end_time - self.start_time).total_seconds()
        print
        print '{}: {}s'.format(self.label, duration)
        print


def _run_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)


def _remove_triggers():
    _run_sql("""
        DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_insert_trigger
            ON core_assignmentgroup;
        DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_insert_or_update_trigger
            ON devilry_group_feedbackset;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_imageannotationcomment_trigger
            ON devilry_group_imageannotationcomment;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_change_trigger
            ON devilry_group_imageannotationcomment;
    """)


@unittest.skip('Bechmark - should just be enabled when debugging performance')
class TestBenchMarkAssignmentGroupFileUploadCountTrigger(test.TestCase):

    def setUp(self):
        _remove_triggers()

    def __create_distinct_comments(self, label):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))

        mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_ADMIN)
        comment_student = mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                     user_role=GroupComment.USER_ROLE_STUDENT)
        comment_examiner = mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                      user_role=GroupComment.USER_ROLE_EXAMINER)

        count = 1000
        with TimeExecution('{} ({})'.format(label, count)):
            for x in range(count):
                student_file = mommy.make(CommentFile, comment=comment_student)
                student_file.file.save('testfile.txt', ContentFile('test'))
                examiner_file = mommy.make(CommentFile, comment=comment_examiner)
                examiner_file.file.save('testfile.txt', ContentFile('test'))
                # student_file.delete()

                # f or c in comments:
                #     c.save()

                # for c in comments:
                #     c.delete()
                #
                # cached_data = AssignmentGroupCachedData.objects.get(group=group)
                # print "feedbackset_count:", cached_data.feedbackset_count
                # print "public_total_comment_count:", cached_data.public_total_comment_count
                # print "public_student_comment_count:", cached_data.public_student_comment_count
                # print "public_examiner_comment_count:", cached_data.public_examiner_comment_count
                # print "public_admin_comment_count:", cached_data.public_admin_comment_count
                #
                #
                # print "file_upload_count_total:", cached_data.file_upload_count_total
                # print "file_upload_count_student:", cached_data.file_upload_count_student
                # print "file_upload_count_examiner:", cached_data.file_upload_count_examiner

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_comments('file upload: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_distinct_comments('file upload: with triggers')


@unittest.skip('Bechmark - should just be enabled when debugging performance')
class TestBenchMarkFeedbackSetTrigger(test.TestCase):

    def setUp(self):
        _remove_triggers()

    def __create_in_distinct_groups_feedbacksets(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)

        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))
        AssignmentGroup.objects.bulk_create(groups)

        feedbacksets = []
        for group in AssignmentGroup.objects.filter(parentnode=assignment):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_distinct_groups_without_triggers(self):
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: no triggers')

    def test_create_feedbacksets_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: with triggers')

    def __create_in_same_group_feedbacksets(self, label):
        count = 1000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        feedbacksets = []
        for x in range(count):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_same_group_without_triggers(self):
        self.__create_in_same_group_feedbacksets('feedbacksets same group: no triggers')

    def test_create_feedbacksets_in_same_group_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        # This should have some overhead because we need to UPDATE the AssignmentGroupCachedData
        # for each INSERT
        self.__create_in_same_group_feedbacksets('feedbacksets same group: with triggers')


@unittest.skip('Bechmark - should just be enabled when debugging performance')
class TestBenchMarkAssignmentGroupTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_distinct_groups(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))

        with TimeExecution('{} ({})'.format(label, count)):
            AssignmentGroup.objects.bulk_create(groups)

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_groups('assignment groups: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_distinct_groups('assignment groups: with triggers')


@unittest.skip('Bechmark - should just be enabled when debugging performance')
class TestBenchMarkAssignmentGroupCommentCountTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_distinct_comments(self, label):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))

        count = 100
        comments = []
        for x in range(count):
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_ADMIN))
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_STUDENT))
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_EXAMINER))

        with TimeExecution('{} ({})'.format(label, count)):
            for c in comments:
                c.save()

                # for c in comments:
                #    c.delete()
                #
        return group

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_comments('assignment groups comments: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        group = self.__create_distinct_comments('assignment groups comments: with triggers')
        cached_data = AssignmentGroupCachedData.objects.get(group=group)
        print "feedbackset_count:", cached_data.feedbackset_count
        print "public_total_comment_count:", cached_data.public_total_comment_count
        print "public_student_comment_count:", cached_data.public_student_comment_count
        print "public_examiner_comment_count:", cached_data.public_examiner_comment_count
        print "public_admin_comment_count:", cached_data.public_admin_comment_count
