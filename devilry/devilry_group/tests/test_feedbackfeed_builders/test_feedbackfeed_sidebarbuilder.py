# Django imports
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

# Devilry imports
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group.feedbackfeed_builder.feedbackfeed_sidebarbuilder import FeedbackFeedSidebarBuilder
from devilry.devilry_group import models as group_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestFeedbackfeedSidebarBuilder(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_num_queries(self):
        # Must be refactored
        # Test that the number of queries performed is manageable
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup')
        testassignment = testgroup.assignment
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=100)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=100)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user=candidate.relatedstudent.user)
        mommy.make('devilry_comment.CommentFile',
                   comment=testcomment,
                   _quantity=100)

        with self.assertNumQueries(8):
            feedbackset_queryset = builder_base.get_feedbackfeed_builder_queryset(testgroup, testuser, 'unused')
            sidebarbuilder = FeedbackFeedSidebarBuilder(
                assignment=testassignment,
                group=testgroup,
                feedbacksets=feedbackset_queryset)
            sidebarbuilder.build()
            sidebarbuilder.get_as_list()
        self.assertEquals(1, group_models.FeedbackSet.objects.count())