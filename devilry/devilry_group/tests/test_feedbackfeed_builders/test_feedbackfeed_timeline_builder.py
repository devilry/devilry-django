# Django imports
from django.test import TestCase
from django.conf import settings

# Third party imports
from django.utils import timezone
from model_bakery import baker

# Devilry imports
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group.feedbackfeed_builder.feedbackfeed_timelinebuilder import FeedbackFeedTimelineBuilder
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet, GroupComment


class TimelineBuilderTestMixin:
    devilryrole = None

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __build_timeline(self, group, user, assignment):
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=group,
            requestuser=user,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=assignment,
            feedbacksets=feedbackset_queryset,
            group=group
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        return timeline_list

    def test_one_feedbackset_unpublished_event(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'], [])

    def test_one_feedbackset_published_event(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['type'], 'grade')
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['grade_points'], testfeedbackset.grading_points)

    def test_feedback_set_merge_type_ordered_before_not_merge_type_feedback_set(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        now = timezone.now()
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end', first_deadline=now)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = baker.make('devilry_group.FeedbackSet',
                                     deadline_datetime=now,
                                     group=testgroup, feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)
        self.assertEqual(timeline_list[1]['feedbackset'], testfeedbackset)

    def test_feedbackset_mergetype_is_excluded_if_not_published_and_no_comments_visible_to_everyone(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = baker.make('devilry_group.FeedbackSet',
                                     group=testgroup, feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1) # Auto created first feedbackset for assignment group.
        self.assertNotEqual(timeline_list[0]['feedbackset'], testfeedbackset)

    def test_feedbackset_mergetype_added_if_published_but_no_comments_visible_to_everyone(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup, feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)

    def test_feedbackset_mergetype_added_if_not_published_but_has_comments_visible_to_everyone(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = baker.make('devilry_group.FeedbackSet',
                   group=testgroup, feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)

    def test_feedbackset_published_grading_points_same_as_first_updated_grading_points(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup)
        first_grading_points_update = baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                                                 old_grading_points=testfeedbackset.grading_points,
                                                 feedback_set=testfeedbackset)
        last_grading_points_update = baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                                                old_grading_points=0,
                                                feedback_set=testfeedbackset)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup,
            requestuser=testuser,
            devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['type'], 'grade')
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['grade_points'],
                             first_grading_points_update.old_grading_points)
        self.assertNotEqual(timeline_list[0]['feedbackset_events'][0]['grade_points'],
                          last_grading_points_update.old_grading_points)

    def test_updated_grading_points_event_no_updates(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        timeline_list = self.__build_timeline(group=testgroup, user=testuser, assignment=testassignment)
        self.assertEqual(len(timeline_list[0]['feedbackset_events']), 1)

    def test_updated_grading_points_event_one_update(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                   old_grading_points=testfeedbackset.grading_points,
                   feedback_set=testfeedbackset)
        timeline_list = self.__build_timeline(group=testgroup, user=testuser, assignment=testassignment)
        self.assertEqual(len(timeline_list[0]['feedbackset_events']), 2)
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['type'], 'grade')
        self.assertEqual(timeline_list[0]['feedbackset_events'][1]['type'], 'grading_updated')
        self.assertEqual(timeline_list[0]['feedbackset_events'][1]['obj'].old_grading_points,
                         testfeedbackset.grading_points)

    def test_updated_grading_points_event_multiple_updates(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                   old_grading_points=testfeedbackset.grading_points,
                   feedback_set=testfeedbackset)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                   old_grading_points=0,
                   feedback_set=testfeedbackset)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory',
                   old_grading_points=1,
                   feedback_set=testfeedbackset)
        timeline_list = self.__build_timeline(group=testgroup, user=testuser, assignment=testassignment)
        self.assertEqual(len(timeline_list[0]['feedbackset_events']), 4)
        self.assertEqual(timeline_list[0]['feedbackset_events'][0]['type'], 'grade')
        self.assertEqual(timeline_list[0]['feedbackset_events'][1]['type'], 'grading_updated')
        self.assertEqual(timeline_list[0]['feedbackset_events'][1]['obj'].old_grading_points, 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'][1]['next_grading_points'], 0)
        self.assertEqual(timeline_list[0]['feedbackset_events'][2]['obj'].old_grading_points, 0)
        self.assertEqual(timeline_list[0]['feedbackset_events'][2]['next_grading_points'], 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'][3]['obj'].old_grading_points, 1)
        self.assertEqual(timeline_list[0]['feedbackset_events'][3]['next_grading_points'], 1)

    def test_merged_feedbackset_without_with_grading_or_public_commnet_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1)
        self.assertEqual(timeline_list[0]['feedbackset'], feedbackset)

    def test_merged_feedbackset_only_with_grading_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)
        self.assertEqual(timeline_list[0]['feedbackset'], merged_feedbackset)
        self.assertEqual(timeline_list[1]['feedbackset'], feedbackset)

    def test_merged_feedbackset_only_with_public_comment_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=merged_feedbackset)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)
        self.assertEqual(timeline_list[0]['feedbackset'], merged_feedbackset)
        self.assertEqual(timeline_list[1]['feedbackset'], feedbackset)


class TestTimelineBuilderStudent(TimelineBuilderTestMixin, TestCase):
    devilryrole = 'student'

    def test_merged_feedbackset_only_internal_notes_not_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=merged_feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 1)
        self.assertEqual(timeline_list[0]['feedbackset'], feedbackset)


class TestTimelineBuilderExaminer(TimelineBuilderTestMixin, TestCase):
    devilryrole = 'examiner'

    def test_merged_feedbackset_only_internal_notes_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=merged_feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)
        self.assertEqual(timeline_list[0]['feedbackset'], merged_feedbackset)
        self.assertEqual(timeline_list[1]['feedbackset'], feedbackset)


class TestTimelineBuilderAdmin(TimelineBuilderTestMixin, TestCase):
    devilryrole = 'admin'

    def test_merged_feedbackset_only_internal_notes_visible(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        merged_feedbackset = baker.make('devilry_group.FeedbackSet',
                                        group=testgroup,
                                        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT)
        baker.make('devilry_group.GroupComment', feedback_set=merged_feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        feedbackset = group_baker.make_first_feedbackset_in_group(group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
            group=testgroup, requestuser=testuser, devilryrole=self.devilryrole
        )
        timeline_builder = FeedbackFeedTimelineBuilder(
            assignment=testassignment,
            feedbacksets=feedbackset_queryset,
            group=testgroup
        )
        timeline_builder.build()
        timeline_list = timeline_builder.get_as_list()
        self.assertEqual(len(timeline_list), 2)
        self.assertEqual(timeline_list[0]['feedbackset'], merged_feedbackset)
        self.assertEqual(timeline_list[1]['feedbackset'], feedbackset)
