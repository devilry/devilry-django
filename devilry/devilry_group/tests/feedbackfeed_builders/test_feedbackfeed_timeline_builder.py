# Django imports
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

# Third party imports
from model_mommy import mommy

# Devilry imports
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.feedbackfeed_builder.feedbackfeed_timelinebuilder import FeedbackFeedTimelineBuilder
from devilry.devilry_group import models as group_models
from devilry.devilry_group.feedbackfeed_builder import builder_base


class TestFeedbackFeedTimelineBuilder(TestCase, object):

    def test_get_last_deadline_one_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet', group=testgroup)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='unused')
        timelinebuilder = FeedbackFeedTimelineBuilder(
                feedbacksets=feedbackset_queryset,
                group=testgroup)
        timelinebuilder.build()
        self.assertEquals(1, len(timelinebuilder.feedbacksets))
        self.assertEquals(testassignment.first_deadline, timelinebuilder.get_last_deadline())

    def test_get_last_deadline_two_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None)
        testfeedbackset_last = mommy.make('devilry_group.FeedbackSet',
                                          group=testgroup,
                                          deadline_datetime=timezone.now(),
                                          feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='unused')
        timelinebuilder = FeedbackFeedTimelineBuilder(feedbacksets=feedbackset_queryset,
                                                      group=testgroup)
        timelinebuilder.build()
        self.assertEquals(2, len(timelinebuilder.feedbacksets))
        self.assertEquals(testfeedbackset_last.deadline_datetime, timelinebuilder.get_last_deadline())

    def test_get_num_elements_in_timeline(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=20),
                grading_published_datetime=now-timezone.timedelta(days=19))
        group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=18),
                deadline_datetime=now-timezone.timedelta(days=17),
                grading_published_datetime=now-timezone.timedelta(days=16))
        group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                is_last_in_group=None,
                created_datetime=now - timezone.timedelta(days=15),
                deadline_datetime=now-timezone.timedelta(days=14),
                grading_published_datetime=now-timezone.timedelta(days=13))
        group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                created_datetime=now - timezone.timedelta(days=12),
                deadline_datetime=now-timezone.timedelta(days=11),
                grading_published_datetime=now-timezone.timedelta(days=10))
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='unused')
        timelinebuilder = FeedbackFeedTimelineBuilder(feedbacksets=feedbackset_queryset,
                                                      group=testgroup)
        timelinebuilder.build()

        self.assertEquals(11, len(timelinebuilder.timeline))

    def test_get_last_feedbackset(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=10))
        testfeedbackset_last = group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                deadline_datetime=now-timezone.timedelta(days=9),
                # is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=8))
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='unused')
        timelinebuilder = FeedbackFeedTimelineBuilder(feedbacksets=feedbackset_queryset,
                                                      group=testgroup)
        timelinebuilder.build()
        self.assertEquals(testfeedbackset_last, timelinebuilder.get_last_feedbackset())

    def test_get_last_deadline(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=10))
        testfeedbackset_last = group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                deadline_datetime=now-timezone.timedelta(days=9),
                # is_last_in_group=None,
                grading_published_datetime=now-timezone.timedelta(days=8))
        testfeedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='unused')
        timelinebuilder = FeedbackFeedTimelineBuilder(feedbacksets=testfeedbackset_queryset,
                                                      group=testgroup)
        timelinebuilder.build()
        self.assertEquals(testfeedbackset_last.deadline_datetime, timelinebuilder.get_last_deadline())

    def test_get_visibility_for_roles_not_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        testexaminer = mommy.make('core.Examiner',
                                  assignmentgroup=testgroup,
                                  relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        testexaminer2 = mommy.make('core.Examiner',
                                   assignmentgroup=testgroup,
                                   relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        testcandidate = mommy.make('core.Candidate',
                                   assignment_group=testgroup,
                                   relatedstudent__user=mommy.make(settings.AUTH_USER_MODEL))

        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=testexaminer.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=testexaminer.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   part_of_grading=True,
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=testcandidate.relatedstudent.user,
                   user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=testcandidate.relatedstudent.user,
                   user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=testexaminer.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=testexaminer.relatedexaminer.user,
                   user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=testfeedbackset)

        # examiner can see all comments
        testexaminer_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testexaminer.relatedexaminer.user,
                devilryrole='unused')
        timelinebuilder_examiner = FeedbackFeedTimelineBuilder(feedbacksets=testexaminer_queryset,
                                                               group=testgroup)
        timelinebuilder_examiner.build()
        self.assertEquals(6, len(timelinebuilder_examiner.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(7, len(timelinebuilder_examiner.timeline))

        # examiner2 can see all comments, except private comments
        testexaminer2_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testexaminer2.relatedexaminer.user,
                devilryrole='examiner')
        timelinebuilder_examiner2 = FeedbackFeedTimelineBuilder(feedbacksets=testexaminer2_queryset,
                                                                group=testgroup)
        timelinebuilder_examiner2.build()
        self.assertEquals(5, len(timelinebuilder_examiner2.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(6, len(timelinebuilder_examiner2.timeline))

        # student can only see what is visible to everyone(VISIBILITY_VISIBLE_TO_EVERYONE)
        testcandidate_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testcandidate.relatedstudent.user,
                devilryrole='student')
        timelinebuilder_student = FeedbackFeedTimelineBuilder(
            feedbacksets=testcandidate_queryset,
            group=testgroup)
        timelinebuilder_student.build()
        self.assertEquals(3, len(timelinebuilder_student.feedbacksets[0].groupcomment_set.all()))
        self.assertEquals(4, len(timelinebuilder_student.timeline))

    def test_get_one_group(self):
        testassignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testassignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        relatedstudent = mommy.make('core.RelatedStudent')
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent=relatedstudent)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent=relatedstudent)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup1,
                requestuser=relatedstudent.user,
                devilryrole='student')
        timelinebuilder = FeedbackFeedTimelineBuilder(
            feedbacksets=feedbackset_queryset,
            group=testgroup1)
        self.assertEquals(1, len(timelinebuilder.feedbacksets))
        self.assertEquals(feedbackset, timelinebuilder.feedbacksets[0])

    def test_complete_example(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = mommy.make('core.Candidate',
                                   assignment_group=testgroup,
                                   relatedstudent__user__fullname='Test User1',
                                   relatedstudent__user__shortname='testuser1@example.com')
        testexaminer = mommy.make('core.Examiner',
                                  assignmentgroup=testgroup,
                                  relatedexaminer_user__fullname='Test User2',
                                  relatedexaminer__user__shortname='testuser2@example.com')

        # First feedbackset published with comments and grading
        testfeedbackset1 = group_mommy.feedbackset_first_attempt_published(
                grading_published_datetime=testassignment.first_deadline + timezone.timedelta(days=1),
                grading_points=10,
                created_by=testexaminer.relatedexaminer.user,
                created_datetime=testassignment.publishing_time,
                is_last_in_group=None,
                group=testgroup,
                grading_published_by=testexaminer.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   created_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
                   published_datetime=testfeedbackset1.current_deadline() - timezone.timedelta(hours=1),
                   user=testcandidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset1)
        mommy.make('devilry_group.GroupComment',
                   created_datetime=testfeedbackset1.current_deadline() + timezone.timedelta(hours=1),
                   published_datetime=testfeedbackset1.current_deadline() + timezone.timedelta(hours=1),
                   user=testexaminer.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=testfeedbackset1)

        # Second feedbackset with comments and grading
        testfeedbackset2 = group_mommy.feedbackset_new_attempt_published(
                grading_published_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(days=4),
                grading_points=10,
                created_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(hours=10),
                deadline_datetime=testfeedbackset1.grading_published_datetime + timezone.timedelta(days=3),
                created_by=testexaminer.relatedexaminer.user,
                group=testgroup,
                grading_published_by=testexaminer.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   created_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
                   published_datetime=testfeedbackset2.current_deadline() - timezone.timedelta(hours=1),
                   user=testcandidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset2)
        mommy.make('devilry_group.GroupComment',
                   created_datetime=testfeedbackset2.current_deadline() + timezone.timedelta(hours=1),
                   published_datetime=testfeedbackset2.current_deadline() + timezone.timedelta(hours=1),
                   user=testexaminer.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=testfeedbackset2)

        feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group=testgroup,
                requestuser=testuser,
                devilryrole='student')
        built_timeline = FeedbackFeedTimelineBuilder(
            feedbacksets=feedbackset_queryset,
            group=testgroup)

        built_timeline.build()
        builder_list = built_timeline.get_as_list()

        self.assertEquals(builder_list[0]['type'], 'comment')
        self.assertEquals(builder_list[1]['type'], 'deadline_expired')
        self.assertEquals(builder_list[2]['type'], 'comment')
        self.assertEquals(builder_list[3]['type'], 'grade')
        self.assertEquals(builder_list[4]['type'], 'deadline_created')
        self.assertEquals(builder_list[5]['type'], 'comment')
        self.assertEquals(builder_list[6]['type'], 'deadline_expired')
        self.assertEquals(builder_list[7]['type'], 'comment')
        self.assertEquals(builder_list[8]['type'], 'grade')
