import mock
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.timeline_builder.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder
from devilry.devilry_group import models as group_models


class TestFeedbackFeedTimelineBuilder(TestCase, object):

    def test_get_last_deadline_one_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.FeedbackSet', group=group)
        timelinebuilder = FeedbackFeedTimelineBuilder(group=group, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()
        self.assertEquals(1, len(timelinebuilder.feedbacksets))
        self.assertEquals(assignment.first_deadline, timelinebuilder.get_last_deadline())

    def test_get_last_deadline_two_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None)
        feedbackset_last = mommy.make('devilry_group.FeedbackSet',
                                      group=group,
                                      deadline_datetime=timezone.now(),
                                      feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        timelinebuilder = FeedbackFeedTimelineBuilder(group=group, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()
        self.assertEquals(2, len(timelinebuilder.feedbacksets))
        self.assertEquals(feedbackset_last.deadline_datetime, timelinebuilder.get_last_deadline())

    def test_get_num_elements_in_timeline(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=group,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=20),
                grading_published_datetime=now-timezone.timedelta(days=19))
        group_mommy.feedbackset_new_attempt_published(
                group=group,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=18),
                deadline_datetime=now-timezone.timedelta(days=17),
                grading_published_datetime=now-timezone.timedelta(days=16))
        group_mommy.feedbackset_new_attempt_published(
                group=group,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=15),
                deadline_datetime=now-timezone.timedelta(days=14),
                grading_published_datetime=now-timezone.timedelta(days=13))
        group_mommy.feedbackset_new_attempt_published(
                group=group,
                created_datetime=now - timezone.timedelta(days=12),
                deadline_datetime=now-timezone.timedelta(days=11),
                grading_published_datetime=now-timezone.timedelta(days=10))
        timelinebuilder = FeedbackFeedTimelineBuilder(group=group, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()

        self.assertEquals(11, len(timelinebuilder.timeline))

    def test_get_last_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=group,
                is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=10))
        feedbackset_last = group_mommy.feedbackset_new_attempt_published(
                group=group,
                deadline_datetime=now-timezone.timedelta(days=9),
                # is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=8))
        timelinebuilder = FeedbackFeedTimelineBuilder(group=group, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()
        self.assertEquals(feedbackset_last, timelinebuilder.get_last_feedbackset())

    def test_get_last_deadline(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=group,
                is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=10))
        feedbackset_last = group_mommy.feedbackset_new_attempt_published(
                group=group,
                deadline_datetime=now-timezone.timedelta(days=9),
                # is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=8))
        timelinebuilder = FeedbackFeedTimelineBuilder(group=group, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()
        self.assertEquals(feedbackset_last.deadline_datetime, timelinebuilder.get_last_deadline())

    def test_get_visibility_for_roles_not_published(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        examiner2 = mommy.make('core.Examiner',
                               assignmentgroup=group,
                               relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent__user=mommy.make(settings.AUTH_USER_MODEL))

        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=feedbackset)

        # examiner can see all comments
        timelinebuilder_examiner = FeedbackFeedTimelineBuilder(
                group=group,
                requestuser=examiner.relatedexaminer.user,
                devilryrole='examiner')
        timelinebuilder_examiner.build()
        self.assertEquals(6, len(timelinebuilder_examiner.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(7, len(timelinebuilder_examiner.timeline))

        # examiner2 can see all comments, except private comments
        timelinebuilder_examiner2 = FeedbackFeedTimelineBuilder(
                group=group,
                requestuser=examiner2.relatedexaminer.user,
                devilryrole='examiner')
        timelinebuilder_examiner2.build()
        self.assertEquals(5, len(timelinebuilder_examiner2.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(6, len(timelinebuilder_examiner2.timeline))

        # student can only see what is visible to everyone(VISIBILITY_VISIBLE_TO_EVERYONE)
        timelinebuilder_student = FeedbackFeedTimelineBuilder(
            group=group,
            requestuser=candidate.relatedstudent.user,
            devilryrole='student'
        )
        timelinebuilder_student.build()
        self.assertEquals(3, len(timelinebuilder_student.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(4, len(timelinebuilder_student.timeline))

    def test_get_one_group(self):
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2)
        relatedstudent = mommy.make('core.RelatedStudent')
        mommy.make('core.Candidate',
                   assignment_group=group1,
                   relatedstudent=relatedstudent)
        mommy.make('core.Candidate',
                   assignment_group=group2,
                   relatedstudent=relatedstudent)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group1)
        group_mommy.feedbackset_first_attempt_unpublished(group=group2)

        timelinebuilder = FeedbackFeedTimelineBuilder(
            group=group1,
            requestuser=relatedstudent.user,
            devilryrole='student'
        )
        self.assertEquals(1, len(timelinebuilder.feedbacksets))
        self.assertEquals(feedbackset, timelinebuilder.feedbacksets[0])