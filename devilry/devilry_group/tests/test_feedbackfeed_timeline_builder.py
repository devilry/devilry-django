import devilry
from django.test import RequestFactory, TestCase
from django.utils import timezone
import htmls
import mock
from model_mommy import mommy
from devilry.devilry_group.views.feedbackfeed_student import StudentFeedbackFeedView
from devilry.devilry_group.views.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder2, AssignmentGroupBuilder, FeedbackSetBuilder, \
    GroupCommentBuilder


class TestFeedbackFeedTimelineBuilder(TestCase, object):
    pass
    # def test_get_feedbacksets_for_group(self):
        # timelinebuilder = FeedbackFeedTimelineBuilder(None)
        # assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        # assignment_group = mommy.make(
        #     'core.AssignmentGroup',
        #     parentnode=assignment,
        #     name='dewey'
        # )
        # feedbackset = mommy.make(
        #     'devilry_group.FeedbackSet',
        #     group=assignment_group,
        #     created_datetime=timezone.now(),
        #     deadline_datetime=timezone.now()+timezone.timedelta(days=11)
        # )
        # feedbackset1 = mommy.make(
        #     'devilry_group.FeedbackSet',
        #     group=assignment_group,
        #     created_datetime=timezone.now(),
        #     deadline_datetime=timezone.now()+timezone.timedelta(days=10)
        # )
        #
        # self.assertEquals(2, len(timelinebuilder.get_feedbacksets_for_group(assignment_group)))