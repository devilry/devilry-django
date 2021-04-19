from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from devilry.devilry_group import models as group_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_dbcache import models as cache_models


class TestDevilryGroupBakeryFactories(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_feedbackset_save(self):
        testgroup = baker.make('core.AssignmentGroup')
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        grading_datetime = timezone.now()
        testfeedbackset = group_models.FeedbackSet.objects.get(group=testgroup)
        devilry_group_baker_factories.feedbackset_save(
                testfeedbackset,
                grading_published_datetime=grading_datetime,
                grading_points=10,
                grading_published_by=examiner.relatedexaminer.user
        )
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        self.assertEqual(testgroup.id, testfeedbackset.group.id)
        self.assertEqual(testfeedbackset.grading_published_datetime, grading_datetime)
        self.assertEqual(testfeedbackset.grading_points, 10)

    def test_feedbackset_first_attempt_published_without_group(self):
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published()
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        self.assertIsNotNone(testfeedbackset.grading_published_datetime)
        self.assertEqual(testfeedbackset.grading_points, 1)
        self.assertIsNotNone(testfeedbackset.grading_published_by)

        # test caching
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testfeedbackset.group)
        self.assertEqual(cached_group.first_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_published_feedbackset, testfeedbackset)

    def test_feedbackset_first_attempt_published_without_grading_datetime(self):
        testgroup = baker.make('core.AssignmentGroup')
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=testgroup,
                grading_published_by=examiner.relatedexaminer.user
        )
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        self.assertEqual(testgroup.id, testfeedbackset.group.id)
        self.assertIsNotNone(testfeedbackset.grading_published_datetime)
        self.assertEqual(testfeedbackset.grading_points, 1)

        # test caching
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testfeedbackset.group)
        self.assertEqual(cached_group.first_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_published_feedbackset, testfeedbackset)

    def test_feedbackset_first_attempt_published_with_grading_datetime(self):
        testgroup = baker.make('core.AssignmentGroup')
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        grading_datetime = timezone.now()
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=testgroup,
                grading_published_datetime=grading_datetime,
                grading_published_by=examiner.relatedexaminer.user
        )
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        self.assertEqual(testgroup.id, testfeedbackset.group.id)
        self.assertEqual(grading_datetime, testfeedbackset.grading_published_datetime)
        self.assertEqual(testfeedbackset.grading_points, 1)

        # test caching
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testfeedbackset.group)
        self.assertEqual(cached_group.first_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_published_feedbackset, testfeedbackset)

    def test_feedbackset_first_attempt_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        self.assertEqual(testgroup.id, testfeedbackset.group.id)
        self.assertIsNone(testfeedbackset.grading_published_by)
        self.assertIsNone(testfeedbackset.grading_published_datetime)
        self.assertIsNone(testfeedbackset.grading_points)

        # test caching
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testfeedbackset.group)
        self.assertEqual(cached_group.first_feedbackset, testfeedbackset)
        self.assertEqual(cached_group.last_feedbackset, testfeedbackset)
        self.assertIsNone(cached_group.last_published_feedbackset)

    def test_feedbackset_new_attempt_published_with_grading_datetime(self):
        testgroup = baker.make('core.AssignmentGroup')
        testfeedbackset_first = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup
        )
        grading_datetime = timezone.now()
        testfeedbackset = devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup,
            grading_published_datetime=grading_datetime,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        self.assertEqual(testfeedbackset_first.group.id, testfeedbackset.group.id)
        self.assertIsNotNone(testfeedbackset.grading_published_by)
        self.assertIsNotNone(testfeedbackset.grading_points)
        self.assertEqual(grading_datetime, testfeedbackset.grading_published_datetime)

        # test caching
        group_cache = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEqual(group_cache.first_feedbackset, testfeedbackset_first)
        self.assertEqual(group_cache.last_feedbackset, testfeedbackset)
        self.assertEqual(group_cache.last_published_feedbackset, testfeedbackset)

    def test_feedbackset_new_attempt_published_without_grading_datetime(self):
        testgroup = baker.make('core.AssignmentGroup')
        testfeedbackset_first = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup
        )
        testfeedbackset = devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=3)
        )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        self.assertEqual(testfeedbackset_first.group.id, testfeedbackset.group.id)
        self.assertIsNotNone(testfeedbackset.grading_published_by)
        self.assertIsNotNone(testfeedbackset.grading_points)
        self.assertIsNotNone(testfeedbackset.grading_published_datetime)

        # test caching
        group_cache = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEqual(group_cache.first_feedbackset, testfeedbackset_first)
        self.assertEqual(group_cache.last_feedbackset, testfeedbackset)
        self.assertEqual(group_cache.last_published_feedbackset, testfeedbackset)

    def test_feedbackset_new_attempt_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup')
        testfeedbackset_first = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup
        )
        testfeedbackset = devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup
        )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        self.assertEqual(testfeedbackset_first.group.id, testfeedbackset.group.id)
        self.assertIsNone(testfeedbackset.grading_published_by)
        self.assertIsNone(testfeedbackset.grading_points)
        self.assertIsNone(testfeedbackset.grading_published_datetime)

        # test caching
        group_cache = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEqual(group_cache.first_feedbackset, testfeedbackset_first)
        self.assertEqual(group_cache.last_feedbackset, testfeedbackset)
        self.assertEqual(group_cache.last_published_feedbackset, testfeedbackset_first)
