# Django imports
from django.test import TestCase
from django.conf import settings

# Third party imports
from model_mommy import mommy

# Devilry imports
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.feedbackfeed_builder.feedbackfeed_timelinebuilder import FeedbackFeedTimelineBuilder
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestTimelineBuilder(TestCase):
    devilryrole = 'student'

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_one_feedbackset_unpublished_event(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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
        self.assertEquals(len(timeline_list), 1)
        self.assertEquals(timeline_list[0]['feedbackset_events'], [])

    def test_one_feedbackset_published_event(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
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
        self.assertEquals(len(timeline_list), 1)
        self.assertEquals(timeline_list[0]['feedbackset_events'][0]['type'], 'grade')


class TestTimelineBuilderExaminer(TestTimelineBuilder):
    devilryrole = 'examiner'


class TestTimelineBuilderAdmin(TestTimelineBuilder):
    devilryrole = 'admin'


