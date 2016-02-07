import mock
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.timeline_builder.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder
from devilry.devilry_group.views.feedbackfeed_admin import AdminFeedbackFeedView
from devilry.devilry_group.views import feedbackfeed_examiner as examiner_views
from devilry.devilry_group.views.feedbackfeed_student import StudentFeedbackFeedView
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