from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.timeline_builder.feedbackfeed_sidebarbuilder import FeedbackFeedSidebarBuilder
from devilry.devilry_group import models as group_models
from devilry.devilry_group.timeline_builder.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder


class TestFeedbackfeedSidebarBuilder(TestCase):

    def test(self):
        # Must be refactored
        # Test that the number of queries performed is manageable
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfbs = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                is_last_in_group=None)
        testfbs1 = devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfbs)
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfbs1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)

        with self.assertNumQueries(6):
            timelinebuilder = FeedbackFeedTimelineBuilder(group=testgroup, requestuser=testuser, devilryrole='unused')
            timelinebuilder.build()

            sidebarbuilder = FeedbackFeedSidebarBuilder(timelinebuilder.feedbacksets)
            sidebarbuilder.build()

    def test_ordering_dictionary(self):
        # Must be refactored
        # Tests the ordered dictionary produced in FeedbackFeedSidebarBuilder
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1),
                is_last_in_group=None)
        testfeedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() + timezone.timedelta(days=2))

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)

        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)

        timelinebuilder = FeedbackFeedTimelineBuilder(group=testgroup, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()

        sidebarbuilder = FeedbackFeedSidebarBuilder(timelinebuilder.feedbacksets)
        sidebarbuilder.build()

        self.assertTrue(sidebarbuilder.file_dict.keys()[0] < sidebarbuilder.file_dict.keys()[1])

    def test_ordering_get_as_list(self):
        # Must be refactored
        # Tests the ordering of FeedbackFeedSidebarBuilder
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1),
                is_last_in_group=None)
        testfeedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now() + timezone.timedelta(days=2))

        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment)

        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset1)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment1)

        timelinebuilder = FeedbackFeedTimelineBuilder(group=testgroup, requestuser=testuser, devilryrole='unused')
        timelinebuilder.build()

        sidebarbuilder = FeedbackFeedSidebarBuilder(timelinebuilder.feedbacksets)
        sidebarbuilder.build()

        sidebarlist = sidebarbuilder.get_as_list()
        self.assertTrue(sidebarlist[0]['feedbackset'].current_deadline() < sidebarlist[1]['feedbackset'].current_deadline())
