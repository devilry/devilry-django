import json
import shutil
from datetime import timedelta

import arrow
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils import timezone
from ievv_opensource.ievv_batchframework.models import BatchOperation
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories as core_baker
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Examiner
from devilry.apps.core.models import deliverytypes, Assignment, RelatedStudent
from devilry.apps.core.models.assignment_group import GroupPopNotCandidateError, AssignmentGroupTag
from devilry.apps.core.models.assignment_group import GroupPopToFewCandidatesError
from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_comment.models import Comment, CommentFile
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group.models import FeedbackSet, GroupComment, ImageAnnotationComment
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.utils.datetimeutils import default_timezone_datetime


class TestAssignmentGroup(TestCase):
    """
    Test AssignmentGroup using the next generation less coupled testing frameworks.
    """

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_anonymous_displayname_empty(self):
        testgroup = baker.make('core.AssignmentGroup')
        self.assertEqual(
            'no students in group'.format(testgroup.id),
            testgroup.get_anonymous_displayname())

    def test_anonymous_displayname(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='test')
        self.assertEqual(
            'test'.format(testgroup.id),
            testgroup.get_anonymous_displayname())

    def test_short_displayname_empty(self):
        testgroup = baker.make('core.AssignmentGroup')
        self.assertEqual(
            'group#{} - no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_short_displayname_empty_anonymous(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertEqual(
            'no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_short_displayname_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studenta')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studentb')
        self.assertEqual({'studenta', 'studentb'}, set(testgroup.short_displayname.split(', ')))

    def test_short_displayname_anonymous_candidates(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='aa')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='bb',)
        self.assertEqual({'aa', 'bb'}, set(testgroup.short_displayname.split(', ')))

    def test_short_displayname_named(self):
        testgroup = baker.make('core.AssignmentGroup', name='My group')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='ignored')
        self.assertEqual('My group', testgroup.short_displayname)

    def test_short_displayname_named_empty(self):
        testgroup = baker.make('core.AssignmentGroup', name='My group')
        self.assertEqual(
            'group#{} - no students in group'.format(testgroup.id),
            testgroup.short_displayname)

    def test_long_displayname_empty(self):
        testgroup = baker.make('core.AssignmentGroup')
        self.assertEqual(
            'group#{} - no students in group'.format(testgroup.id),
            testgroup.long_displayname)

    def test_long_displayname_empty_anonymous(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertEqual(
            'no students in group',
            testgroup.long_displayname)

    def test_long_displayname_candidates(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__fullname='Student \u00E5')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='studentb')
        self.assertEqual({'Student \u00E5', 'studentb'}, set(testgroup.long_displayname.split(', ')))

    def test_long_displayname_anonymous_candidates(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='aa')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__candidate_id='bb',)
        self.assertEqual({'aa', 'bb'}, set(testgroup.long_displayname.split(', ')))

    def test_long_displayname_named(self):
        testgroup = baker.make('core.AssignmentGroup', name='My group')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__fullname='Student \u00E5')
        self.assertEqual('My group (Student \u00E5)', testgroup.long_displayname)

    def test_long_displayname_named_empty(self):
        testgroup = baker.make('core.AssignmentGroup', name='My group')
        self.assertEqual(
            'My group (group#{} - no students in group)'.format(testgroup.id),
            testgroup.long_displayname)

    def test_last_feedbackset_is_published(self):
        testassignment = baker.make('core.Assignment', passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now(),  # -> published=True
                   deadline_datetime=timezone.now(),
                   grading_points=1)

        self.assertTrue(testgroup.last_feedbackset_is_published)

        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_points=1)

        testgroup.cached_data.refresh_from_db()  # Update cached data from database
        self.assertFalse(testgroup.last_feedbackset_is_published)

    def test_delete_copied_from_does_not_delete_group(self):
        group1 = baker.make('core.AssignmentGroup')
        group2 = baker.make('core.AssignmentGroup', copied_from=group1)
        group1.delete()
        group2 = AssignmentGroup.objects.get(id=group2.id)
        self.assertIsNone(group2.copied_from)

    def test_bulk_create_groups_creates_group(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        self.assertEqual(1, AssignmentGroup.objects.count())

    def test_bulk_create_groups_returns_created_groups(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        created_groups_queryset = AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=[relatedstudent])
        self.assertEqual(1, created_groups_queryset.count())
        self.assertEqual(list(created_groups_queryset), [AssignmentGroup.objects.first()])

    def test_bulk_create_groups_creates_batchoperation_for_group(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        self.assertEqual(1, BatchOperation.objects.count())
        created_group = AssignmentGroup.objects.first()
        created_batchoperation = BatchOperation.objects.first()
        self.assertEqual(created_batchoperation, created_group.batchoperation)

    def test_bulk_create_groups_creates_candidate(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=[relatedstudent])
        created_group = AssignmentGroup.objects.first()
        self.assertEqual(1, created_group.candidates.count())
        created_candidate = Candidate.objects.first()
        self.assertEqual(relatedstudent, created_candidate.relatedstudent)

    def test_bulk_create_groups_creates_feedbackset(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudents = []
        for i in range(5):
            relatedstudents.append(baker.make('core.RelatedStudent',
                                    period=testperiod))
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        group_list = list(AssignmentGroup.objects.bulk_create_groups(created_by_user=testuser,
                                                   assignment=testassignment,
                                                   relatedstudents=relatedstudents))

        self.assertEqual(5, FeedbackSet.objects.all().count())

        for group in AssignmentGroup.objects.all():
            self.assertEqual(1, group.feedbackset_set.count())

        for created_feedbackset in FeedbackSet.objects.all():
            self.assertEqual(testuser, created_feedbackset.created_by)
            self.assertIsNotNone(created_feedbackset.deadline_datetime)

    def test_bulk_create_groups_multiple(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent3 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=[relatedstudent1, relatedstudent2, relatedstudent3])
        self.assertEqual(3, AssignmentGroup.objects.count())
        self.assertEqual(3, Candidate.objects.count())
        self.assertEqual(3, FeedbackSet.objects.count())
        self.assertEqual(1, BatchOperation.objects.count())

        created_candidates = list(Candidate.objects.all())
        self.assertEqual(
                3,
                len({created_candidates[0].assignment_group,
                     created_candidates[1].assignment_group,
                     created_candidates[2].assignment_group}))

        created_feedbacksets = list(FeedbackSet.objects.all())
        self.assertEqual(
                3,
                len({created_feedbacksets[0].group,
                     created_feedbacksets[1].group,
                     created_feedbacksets[2].group}))

    def test_bulk_create_groups_num_queries(self):
        # Trigger ContentType caching so we do not get an extra lookup in the
        # assertNumQueries() statement below.
        ContentType.objects.get_for_model(Assignment)

        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        relatedstudents = list(RelatedStudent.objects.select_related('user'))
        self.assertEqual(20, len(relatedstudents))
        with self.assertNumQueries(6):
            AssignmentGroup.objects.bulk_create_groups(
                created_by_user=testuser,
                assignment=testassignment,
                relatedstudents=relatedstudents)

    def test_filter_has_passing_grade(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        passingfeedbackset = baker.make('devilry_group.FeedbackSet',
                                        deadline_datetime=timezone.now(),
                                        grading_published_datetime=timezone.now(),
                                        group__parentnode=testassignment,
                                        grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   deadline_datetime=timezone.now(),
                   grading_published_datetime=timezone.now(),
                   grading_points=0)
        self.assertEqual(
            [passingfeedbackset.group],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now(),
                   group__parentnode=testassignment,
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored_but_has_older_published(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testgroup],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering1(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   deadline_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=0)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   deadline_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_points=0)
        self.assertEqual(
            [testgroup],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering2(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_points=0)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   deadline_datetime=timezone.now(),
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_not_within_assignment(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   deadline_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(AssignmentGroup.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_user_is_candidate(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.AssignmentGroup')
        group = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   assignment_group=group,
                   relatedstudent__user=testuser)
        self.assertEqual(
            [group],
            list(AssignmentGroup.objects.filter_user_is_candidate(user=testuser)))

    def test_filter_user_is_examiner(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.AssignmentGroup')
        group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=group,
                   relatedexaminer__user=testuser)
        self.assertEqual(
            [group],
            list(AssignmentGroup.objects.filter_user_is_examiner(user=testuser)))


class TestAssignmentGroupMerge(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_merge_not_part_of_same_assignment(self):
        testassignment1 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testassignment2 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        with self.assertRaises(ValidationError):
            AssignmentGroup.merge_groups([testgroup1, testgroup2, testgroup3])

    def test_candidate_foreign_key_is_moved(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        core_baker.candidate(group=group2)
        core_baker.candidate(group=group2)
        AssignmentGroup.merge_groups([group1, group2])
        candidates = Candidate.objects.filter(assignment_group=group1).count()
        self.assertEqual(candidates, 2)

    def test_duplicate_candidate_is_not_merged_and_removed(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        relatedstudent = baker.make('core.RelatedStudent')
        baker.make('candidate', assignment_group=group1, relatedstudent=relatedstudent)
        testcandidate = baker.make('candidate', assignment_group=group2, relatedstudent=relatedstudent)
        candidates = Candidate.objects.filter(assignment_group=group1)
        self.assertEqual(len(candidates), 1)
        AssignmentGroup.merge_groups([group1, group2])
        candidates = Candidate.objects.filter(assignment_group=group1)
        self.assertEqual(len(candidates), 1)
        with self.assertRaises(Candidate.DoesNotExist):
            Candidate.objects.get(id=testcandidate.id)

    def test_examiners_is_merged(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        core_baker.examiner(group=group2, fullname='Thor')
        core_baker.examiner(group=group2, fullname='Odin')
        AssignmentGroup.merge_groups([group1, group2])
        examiners = group1.examiners.all().order_by('relatedexaminer__user__fullname')
        examiner_names = [examiner.relatedexaminer.user.fullname for examiner in examiners]
        self.assertListEqual(examiner_names, ['Odin', 'Thor'])

    def test_duplicate_examiner_is_not_merged_and_removed(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        related_examiner = baker.make('core.RelatedExaminer', user__fullname='Thor')
        baker.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=group1)
        duplicate_examiner = baker.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup=group2)
        core_baker.examiner(group=group2, fullname='Odin')
        AssignmentGroup.merge_groups([group1, group2])
        examiners = group1.examiners.all().order_by('relatedexaminer__user__fullname')
        examiner_names = [examiner.relatedexaminer.user.fullname for examiner in examiners]
        self.assertListEqual(examiner_names, ['Odin', 'Thor'])
        with self.assertRaises(Examiner.DoesNotExist):
            Examiner.objects.get(id=duplicate_examiner.id)

    def test_tags_is_merged(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.AssignmentGroupTag', assignment_group=group2, tag='AAA')
        baker.make('core.AssignmentGroupTag', assignment_group=group2, tag='QQQ')
        AssignmentGroup.merge_groups([group1, group2])
        tags = AssignmentGroupTag.objects.filter(assignment_group=group1).order_by('tag')
        tag_name = [tag.tag for tag in tags]
        self.assertListEqual(tag_name, ['AAA', 'QQQ'])

    def test_tag_duplicate_is_not_merged_and_removed(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.AssignmentGroupTag', assignment_group=group1, tag='AAA')
        duplicate_tag = baker.make('core.AssignmentGroupTag', assignment_group=group2, tag='AAA')
        baker.make('core.AssignmentGroupTag', assignment_group=group2, tag='QQQ')
        AssignmentGroup.merge_groups([group1, group2])
        tags = AssignmentGroupTag.objects.filter(assignment_group=group1).order_by('tag')
        tag_name = [tag.tag for tag in tags]
        self.assertListEqual(tag_name, ['AAA', 'QQQ'])
        with self.assertRaises(AssignmentGroupTag.DoesNotExist):
            AssignmentGroupTag.objects.get(id=duplicate_tag.id)

    def test_cannot_merge_less_than_2_groups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        targetassignmentgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(ValidationError):
            AssignmentGroup.merge_groups([targetassignmentgroup])

    def test_merge_type_first_attempt(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        AssignmentGroup.merge_groups([group1, group2, group3])
        merged_feedbacksets = FeedbackSet.objects.filter(
            group=group1,
            feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT).count()
        self.assertEqual(merged_feedbacksets, 4)

    def test_merge_type_new_attempt(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_new_attempt_published(group=group2)
        group_baker.feedbackset_new_attempt_published(group=group3)
        AssignmentGroup.merge_groups([group1, group2, group3])
        merged_feedbacksets = FeedbackSet.objects.filter(
            group=group1,
            feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT).count()
        self.assertEqual(merged_feedbacksets, 2)

    def test_merge_type_re_edit(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('devilry_group.FeedbackSet',
                   group=group2,
                   deadline_datetime=group2.cached_data.first_feedbackset.current_deadline(),
                   grading_points=1,
                   grading_published_datetime=timezone.now(),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT)
        baker.make('devilry_group.FeedbackSet',
                   group=group3,
                   deadline_datetime=group3.cached_data.first_feedbackset.current_deadline(),
                   grading_points=1,
                   grading_published_datetime=timezone.now(),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT)
        AssignmentGroup.merge_groups([group1, group2, group3])
        merged_feedbacksets = FeedbackSet.objects.filter(
            group=group1,
            feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_RE_EDIT).count()
        self.assertEqual(merged_feedbacksets, 2)

    def test_merge_unpublished_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_new_attempt_unpublished(group=group2)
        group_baker.feedbackset_new_attempt_unpublished(group=group3)
        AssignmentGroup.merge_groups([group1, group2, group3])
        merged_feedbacksets = FeedbackSet.objects.filter(
            group=group1,
            feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT,
            grading_published_datetime=None).count()
        self.assertEqual(merged_feedbacksets, 2)


class TestAssignmentGroupPopCandidate(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def make_test_data(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        testcandidate1 = core_baker.candidate(group=testgroup1)
        testcandidate2 = core_baker.candidate(group=testgroup1)
        core_baker.examiner(group=testgroup1)
        core_baker.examiner(group=testgroup1)
        core_baker.examiner(group=testgroup1)
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup1, tag='AAA')
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup1, tag='DDD')
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup1, tag='QQQ')
        feedbacksets = []
        feedbacksets.append(group_baker.feedbackset_first_attempt_published(testgroup1))
        feedbacksets.append(group_baker.feedbackset_new_attempt_published(testgroup1))
        feedbacksets.append(group_baker.feedbackset_new_attempt_unpublished(testgroup1))

        for feedbackset in feedbacksets:
            for index in range(3):
                comment = baker.make('devilry_group.GroupComment',
                                     feedback_set=feedbackset,
                                     user=testcandidate1.relatedstudent.user,
                                     user_role=GroupComment.USER_ROLE_STUDENT,
                                     text='imba{}'.format(index+200))
                testcommentfile1 = baker.make('devilry_comment.CommentFile', filename='testfile1.txt', comment=comment)
                testcommentfile1.file.save('testfile1.txt', ContentFile('test1'))
                testcommentfile2 = baker.make('devilry_comment.CommentFile', filename='testfile2.txt', comment=comment)
                testcommentfile2.file.save('testfile2.txt', ContentFile('test2'))

            for index in range(3):
                baker.make('devilry_group.GroupComment',
                           feedback_set=feedbackset,
                           user=testcandidate2.relatedstudent.user,
                           user_role=GroupComment.USER_ROLE_STUDENT,
                           text='lol{}'.format(index+100))

            for index in range(7):
                baker.make('devilry_group.GroupComment',
                           feedback_set=feedbackset,
                           user_role=GroupComment.USER_ROLE_EXAMINER,
                           text='cool{}'.format(index+7))

        return (testgroup1, testcandidate1, testcandidate2)

    def test_pop_candidate_not_part_of_assignmentgroup(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        core_baker.candidate(group=testgroup1)
        testcandidate = core_baker.candidate(group=testgroup2)
        with self.assertRaises(GroupPopNotCandidateError):
            testgroup1.pop_candidate(testcandidate)

    def test_pop_candidate_when_there_is_only_one(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = core_baker.candidate(group=testgroup)
        with self.assertRaises(GroupPopToFewCandidatesError):
            testgroup.pop_candidate(testcandidate)

    def test_pop_candidate_has_left_from_assignment_group(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()

        testgroup1.pop_candidate(testcandidate2)

        # testgroup1 contains 1 candidate
        # testgroup1.cached_data.refresh_from_db()
        self.assertEqual(testgroup1.cached_data.candidate_count, 1)
        self.assertFalse(testgroup1.candidates.filter(id=testcandidate2.id).exists())

        # testgroup1 and testgroup2 is different
        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group
        self.assertNotEqual(testgroup1, testgroup2)

        # testgroup2 contains 1 candidate
        self.assertEqual(testgroup2.cached_data.candidate_count, 1)
        self.assertFalse(testgroup2.candidates.filter(id=testcandidate1.id).exists())

    def test_pop_candidate_first_feedbackset_cointains_equal_amount_of_comments(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()

        testgroup1.pop_candidate(testcandidate2)

        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group

        groupcomments1 = GroupComment.objects.filter(feedback_set=testgroup1.cached_data.first_feedbackset)
        groupcomments2 = GroupComment.objects.filter(feedback_set=testgroup2.cached_data.first_feedbackset)
        self.assertEqual(len(groupcomments1), len(groupcomments2))

    def test_pop_candiate_multiple_feedbacksets_with_comments(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()

        testgroup1.pop_candidate(testcandidate2)
        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group
        self.assertNotEqual(testgroup1, testgroup2)
        feedbacksets1 = FeedbackSet.objects.filter(group=testgroup1).order_by_deadline_datetime()
        feedbacksets2 = FeedbackSet.objects.filter(group=testgroup2).order_by_deadline_datetime()

        for feedbackset1, feedbackset2 in zip(feedbacksets1, feedbacksets2):
            groupcomments1 = GroupComment.objects.filter(feedback_set=feedbackset1).order_by('created_datetime')
            groupcomments2 = GroupComment.objects.filter(feedback_set=feedbackset2).order_by('created_datetime')
            self.assertEqual(len(groupcomments1), 13)
            self.assertEqual(len(groupcomments2), 13)

            for comment1, comment2 in zip(groupcomments1, groupcomments2):
                self.assertEqual(comment1.text, comment2.text)

    def test_examiners_has_been_copied_to_new_group(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()
        testgroup1.pop_candidate(testcandidate2)
        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group

        examiners1 = testgroup1.examiners.all().order_by('relatedexaminer__user__id')
        examiners2 = testgroup2.examiners.all().order_by('relatedexaminer__user__id')

        for examiner1, examiner2 in zip(examiners1, examiners2):
            self.assertEqual(examiner1.relatedexaminer, examiner2.relatedexaminer)

    def test_tags_has_been_copied_to_new_group(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()
        testgroup1.pop_candidate(testcandidate2)
        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group

        tags1 = testgroup1.tags.all().order_by('tag')
        tags2 = testgroup2.tags.all().order_by('tag')

        for tag1, tag2 in zip(tags1, tags2):
            self.assertEqual(tag1.tag, tag2.tag)

    def test_commentfile_has_been_copied_into_new_group(self):
        testgroup1, testcandidate1, testcandidate2 = self.make_test_data()
        testgroup1.pop_candidate(testcandidate2)
        testgroup2 = Candidate.objects.get(id=testcandidate2.id).assignment_group

        feedbacksets1 = FeedbackSet.objects.filter(group=testgroup1).order_by_deadline_datetime()
        feedbacksets2 = FeedbackSet.objects.filter(group=testgroup2).order_by_deadline_datetime()
        for feedbackset1, feedbackset2 in zip(feedbacksets1, feedbacksets2):
            groupcomments1 = GroupComment.objects.filter(feedback_set=feedbackset1).order_by('created_datetime')
            groupcomments2 = GroupComment.objects.filter(feedback_set=feedbackset2).order_by('created_datetime')
            for comment1, comment2 in zip(groupcomments1, groupcomments2):
                commentfiles1 = CommentFile.objects.filter(comment=comment1).order_by('filename')
                commentfiles2 = CommentFile.objects.filter(comment=comment2).order_by('filename')
                for commentfile1, commentfile2 in zip(commentfiles1, commentfiles2):
                    self.assertEqual(commentfile1.file, commentfile2.file)
                    self.assertEqual(commentfile1.filename, commentfile2.filename)
                    self.assertEqual(commentfile1.file.path, commentfile2.file.path)


class TestAssignmentGroupGetCurrentState(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_candidate_ids(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate1 = core_baker.candidate(group=testgroup).relatedstudent.user.id
        candidate2 = core_baker.candidate(group=testgroup).relatedstudent.user.id
        candidate3 = core_baker.candidate(group=testgroup).relatedstudent.user.id
        state = testgroup.get_current_state()
        self.assertListEqual(state['candidates'], [candidate1, candidate2, candidate3])

    def test_examiner_ids(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        examiner1 = core_baker.examiner(group=testgroup).relatedexaminer.user.id
        examiner2 = core_baker.examiner(group=testgroup).relatedexaminer.user.id
        examiner3 = core_baker.examiner(group=testgroup).relatedexaminer.user.id
        state = testgroup.get_current_state()
        self.assertIn(examiner1, state['examiners'])
        self.assertIn(examiner2, state['examiners'])
        self.assertIn(examiner3, state['examiners'])

    def test_tags(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup, tag='awesome')
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup, tag='cool')
        baker.make('core.AssignmentGroupTag', assignment_group=testgroup, tag='imba')
        state = testgroup.get_current_state()
        self.assertListEqual(state['tags'], ['awesome', 'cool', 'imba'])

    def test_name(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        state = testgroup.get_current_state()
        self.assertEqual(state['name'], 'group1')

    def test_created_default_timezone_datetime(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        state = testgroup.get_current_state()
        self.assertEqual(state['created_datetime'], testgroup.created_datetime.isoformat())

    def test_parentnode(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=10)
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        state = testgroup.get_current_state()
        self.assertEqual(state['parentnode'], 10)

    def test_feedbacksets(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        feedbacksets = []
        feedbacksets.append(group_baker.feedbackset_first_attempt_published(testgroup).id)
        feedbacksets.append(group_baker.feedbackset_new_attempt_published(testgroup).id)
        feedbacksets.append(group_baker.feedbackset_new_attempt_unpublished(testgroup).id)
        state = testgroup.get_current_state()
        state_feedbacksets_ids = [id for id in state['feedbacksets']]
        self.assertListEqual(state_feedbacksets_ids, feedbacksets)

    def test_is_json_serializeable(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        core_baker.candidate(group=testgroup)
        core_baker.candidate(group=testgroup)
        core_baker.examiner(group=testgroup)
        core_baker.examiner(group=testgroup)
        group_baker.feedbackset_first_attempt_published(testgroup)
        group_baker.feedbackset_new_attempt_published(testgroup)
        state = testgroup.get_current_state()
        json.dumps(state)


class TestAssignmentGroupManager(TestCase):
    def test_filter_is_published(self):
        periodbuilder = SubjectBuilder.quickadd_ducku_duck1010()\
            .add_period('period1',
                        start_time=arrow.get(timezone.now()).replace(days=-60).datetime,
                        end_time=arrow.get(timezone.now()).replace(days=+60).datetime)
        group1 = periodbuilder.add_assignment('assignment1',
                                              publishing_time=arrow.get(timezone.now()).replace(days=-30).datetime)\
            .add_group().group
        periodbuilder.add_assignment('assignment2',
                                     publishing_time=arrow.get(timezone.now()).replace(days=+10).datetime)\
            .add_group()
        periodbuilder.add_assignment('assignment3',
                                     publishing_time=arrow.get(timezone.now()).replace(days=+50).datetime)\
            .add_group()
        qry = AssignmentGroup.objects.filter_is_published()
        self.assertEqual(qry.count(), 1)
        self.assertEqual(qry[0], group1)

    def test_filter_student_has_access(self):
        student1 = UserBuilder('student1').user
        otherstudent = UserBuilder('otherstudent').user
        periodbuilder = SubjectBuilder.quickadd_ducku_duck1010()\
            .add_period('period1',
                        start_time=arrow.get(timezone.now()).replace(days=-60).datetime,
                        end_time=arrow.get(timezone.now()).replace(days=+60).datetime)
        group1 = periodbuilder.add_assignment('assignment1',
                                              publishing_time=arrow.get(timezone.now()).replace(days=-30).datetime)\
            .add_group(students=[student1]).group
        periodbuilder.add_assignment('assignment2',
                                     publishing_time=arrow.get(timezone.now()).replace(days=-10).datetime)\
            .add_group(students=[otherstudent])
        periodbuilder.add_assignment('assignment3',
                                     publishing_time=arrow.get(timezone.now()).replace(days=+50).datetime)\
            .add_group(students=[student1])
        qry = AssignmentGroup.objects.filter_student_has_access(student1)
        self.assertEqual(qry.count(), 1)
        self.assertEqual(qry[0], group1)

    def test_filter_is_active(self):
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        currentgroupbuilder = duck1010builder.add_6month_active_period()\
            .add_assignment('week1').add_group()

        # Add inactive groups to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1').add_group()
        duck1010builder.add_6month_nextyear_period().add_assignment('week1').add_group()

        qry = AssignmentGroup.objects.filter_is_active()
        self.assertEqual(qry.count(), 1)
        self.assertEqual(qry[0], currentgroupbuilder.group)


class TestAssignmentGroupQuerySetPeriodTagFiltering(TestCase):

    #
    # filter_no_periodtag_for_students
    #
    def test_filter_no_periodtag_for_students_no_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_students())

    def test_filter_no_periodtag_for_students_has_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedstudents.add(teststudent.relatedstudent)
        self.assertNotIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_students())

    def test_filter_no_periodtag_for_students_multistudent_group_no_tags(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_students())

    def test_filter_no_periodtag_for_students_multistudent_group_one_student_missing_tags(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedstudents.add(teststudent.relatedstudent)
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_students())

    def test_filter_no_periodtag_for_students_multistudent_group_all_students_has_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent1 = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        teststudent2 = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedstudents.add(teststudent1.relatedstudent)
        testtag.relatedstudents.add(teststudent2.relatedstudent)
        self.assertNotIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_students())

    #
    # filter_periodtag_for_students
    #
    def test_filter_periodtag_for_students_no_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_students_has_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedstudents.add(teststudent.relatedstudent)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_students_has_other_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag1 = baker.make('core.PeriodTag')
        testtag2 = baker.make('core.PeriodTag')
        testtag2.relatedstudents.add(teststudent.relatedstudent)
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag1.id)
        )

    def test_filter_periodtag_for_students_multistudent_group_all_students_missing_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_students_multistudent_group_one_student_missing_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedstudents.add(teststudent.relatedstudent)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_students_multistudent_group_all_students_has_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        teststudent1 = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        teststudent2 = baker.make(
            'core.Candidate',
            assignment_group=testgroup,
            relatedstudent=baker.make('core.RelatedStudent', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedstudents.add(teststudent1.relatedstudent)
        testtag.relatedstudents.add(teststudent2.relatedstudent)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_students(periodtag_id=testtag.id)
        )


    #
    # filter_no_periodtag_for_examiners
    #
    def test_filter_no_periodtag_for_examiners_no_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_examiners())

    def test_filter_no_periodtag_for_examiners_has_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedexaminers.add(testexaminer.relatedexaminer)
        self.assertNotIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_examiners())

    def test_filter_no_periodtag_for_examiners_multiexaminer_group_no_tags(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_examiners())

    def test_filter_no_periodtag_for_examiners_multiexaminer_group_one_examiner_missing_tags(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedexaminers.add(testexaminer.relatedexaminer)
        self.assertIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_examiners())

    def test_filter_no_periodtag_for_examiners_multiexaminer_group_all_examiners_has_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer1 = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testexaminer2 = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag', period=testperiod)
        testtag.relatedexaminers.add(testexaminer1.relatedexaminer)
        testtag.relatedexaminers.add(testexaminer2.relatedexaminer)
        self.assertNotIn(testgroup, AssignmentGroup.objects.filter_no_periodtag_for_examiners())

    #
    # filter_periodtag_for_examiners
    #
    def test_filter_periodtag_for_examiners_no_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_examiners_has_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedexaminers.add(testexaminer.relatedexaminer)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_examiners_has_other_tag_sanity(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag1 = baker.make('core.PeriodTag')
        testtag2 = baker.make('core.PeriodTag')
        testtag2.relatedexaminers.add(testexaminer.relatedexaminer)
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag1.id)
        )

    def test_filter_periodtag_for_examiners_multiexaminer_group_all_examiners_missing_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        self.assertNotIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_examiners_multiexaminer_group_one_examiner_missing_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedexaminers.add(testexaminer.relatedexaminer)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag.id)
        )

    def test_filter_periodtag_for_examiners_multiexaminer_group_all_examiners_has_tag(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testexaminer1 = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testexaminer2 = baker.make(
            'core.Examiner',
            assignmentgroup=testgroup,
            relatedexaminer=baker.make('core.RelatedExaminer', period=testperiod)
        )
        testtag = baker.make('core.PeriodTag')
        testtag.relatedexaminers.add(testexaminer1.relatedexaminer)
        testtag.relatedexaminers.add(testexaminer2.relatedexaminer)
        self.assertIn(
            testgroup,
            AssignmentGroup.objects.filter_periodtag_for_examiners(periodtag_id=testtag.id)
        )



class TestAssignmentGroupQuerySetFilterExaminerHasAccess(TestCase):
    def test_not_examiner_for_any_groups(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(
                0,
                AssignmentGroup.objects.filter_examiner_has_access(user=testuser).count())

    def test_examiner_for_group_but_not_active(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user=testuser,
                   relatedexaminer__active=False)
        self.assertEqual(
                0,
                AssignmentGroup.objects.filter_examiner_has_access(user=testuser).count())

    def test_examiner_for_group_and_active_but_in_old_period(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user=testuser,
                   relatedexaminer__active=True)
        self.assertEqual(
                0,
                AssignmentGroup.objects.filter_examiner_has_access(user=testuser).count())

    def test_examiner_for_group_and_active_but_in_future_period(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user=testuser,
                   relatedexaminer__active=True)
        self.assertEqual(
                0,
                AssignmentGroup.objects.filter_examiner_has_access(user=testuser).count())

    def test_examiner_for_group_and_active(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user=testuser,
                   relatedexaminer__active=True)
        self.assertEqual(
                1,
                AssignmentGroup.objects.filter_examiner_has_access(user=testuser).count())


class TestAssignmentGroupQuerySetExtraOrdering(TestCase):
    def test_extra_annotate_with_fullname_of_first_candidate_shortnameonly(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.fullname_of_first_candidate)

    def test_extra_annotate_with_fullname_of_first_candidate_fullname(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   relatedstudent__user__fullname='User B',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   relatedstudent__user__fullname='User A',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate().first()
        self.assertEqual('user ausera', annotatedgroup.fullname_of_first_candidate)

    def test_extra_annotate_with_fullname_of_first_candidate_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_fullname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).fullname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).fullname_of_first_candidate)

    def test_extra_order_by_fullname_of_first_candidate_ascending_shortnames(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_descending_shortnames(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_ascending_fullnames(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__fullname='BUser1',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='buser2',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user3',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user4',
                   relatedstudent__user__fullname='AUser4',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate())
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_fullname_of_first_candidate_descending_fullnames(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__fullname='BUser1',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='buser2',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user3',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='user4',
                   relatedstudent__user__fullname='AUser4',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_fullname_of_first_candidate(descending=True))
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_anonymousid(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate().first()
        self.assertEqual('anonymousa',
                         annotatedgroup.relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_candidateid(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   relatedstudent__candidate_id='candidatex',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   relatedstudent__candidate_id='candidatey',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate().first()
        self.assertEqual('candidatexanonymousb',
                         annotatedgroup.relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects\
            .extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate()
        self.assertEqual('anonymousa',
                         queryset.get(id=testgroup1.id).relatedstudents_anonymous_id_of_first_candidate)
        self.assertEqual('anonymousx',
                         queryset.get(id=testgroup2.id).relatedstudents_anonymous_id_of_first_candidate)

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_ascending_anonymousids(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_descending_anonymousids(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_ascending_candidateids(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='a',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='b',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='c',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='d',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_relatedstudents_anonymous_id_of_first_candidate_descending_candidateids(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='a',
                   relatedstudent__automatic_anonymous_id='anonymousb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='b',
                   relatedstudent__automatic_anonymous_id='anonymousa',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='c',
                   relatedstudent__automatic_anonymous_id='anonymousx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__candidate_id='d',
                   relatedstudent__automatic_anonymous_id='anonymousy',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_candidates_candidate_id_of_first_candidate(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='candidatex',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   candidate_id='candidatey',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects\
            .extra_annotate_with_candidates_candidate_id_of_first_candidate().first()
        self.assertEqual('candidatex',
                         annotatedgroup.candidates_candidate_id_of_first_candidate)

    def test_extra_annotate_with_candidates_candidate_id_of_first_candidate_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='candidateb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   candidate_id='candidatea',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='candidatex',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   candidate_id='candidatey',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects\
            .extra_annotate_with_candidates_candidate_id_of_first_candidate()
        self.assertEqual('candidatea',
                         queryset.get(id=testgroup1.id).candidates_candidate_id_of_first_candidate)
        self.assertEqual('candidatex',
                         queryset.get(id=testgroup2.id).candidates_candidate_id_of_first_candidate)

    def test_extra_order_by_candidates_candidate_id_of_first_candidate_ascending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='a',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   candidate_id='b',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='c',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   candidate_id='d',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_candidates_candidate_id_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_candidates_candidate_id_of_first_candidate_descending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='a',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   candidate_id='b',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   candidate_id='c',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   candidate_id='d',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_candidates_candidate_id_of_first_candidate(
            descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_shortname_of_first_candidate(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_shortname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.shortname_of_first_candidate)

    def test_extra_annotate_with_shortname_of_first_candidate_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_shortname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).shortname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).shortname_of_first_candidate)

    def test_extra_order_by_shortname_of_first_candidate_ascending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_shortname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_shortname_of_first_candidate_descending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__shortname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_shortname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])

    def test_extra_annotate_with_lastname_of_first_candidate(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup)
        annotatedgroup = AssignmentGroup.objects.extra_annotate_with_lastname_of_first_candidate().first()
        self.assertEqual('usera', annotatedgroup.lastname_of_first_candidate)

    def test_extra_annotate_with_lastname_of_first_candidate_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        queryset = AssignmentGroup.objects.extra_annotate_with_lastname_of_first_candidate()
        self.assertEqual('usera', queryset.get(id=testgroup1.id).lastname_of_first_candidate)
        self.assertEqual('userx', queryset.get(id=testgroup2.id).lastname_of_first_candidate)

    def test_extra_order_by_lastname_of_first_candidate_ascending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_lastname_of_first_candidate())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup2, groups[1])

    def test_extra_order_by_lastname_of_first_candidate_descending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userb',
                   assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usera',
                   assignment_group=testgroup1)
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='userx',
                   assignment_group=testgroup2)
        baker.make('core.Candidate',
                   relatedstudent__user__lastname='usery',
                   assignment_group=testgroup2)
        groups = list(AssignmentGroup.objects.extra_order_by_lastname_of_first_candidate(descending=True))
        self.assertEqual(testgroup2, groups[0])
        self.assertEqual(testgroup1, groups[1])


class TestAssignmentGroupIsWaitingForFeedback(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_feedback_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_published_datetime=ACTIVE_PERIOD_START)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_feedback)

    def test_false_deadline_not_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_END)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_feedback)

    def test_false_deadline_not_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_END)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_feedback)

    def test_true_deadline_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_feedback)

    def test_true_deadline_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_feedback)

    def test_true_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=10))
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_feedback)


class TestAssignmentGroupQuerySetAnnotateWithIsWaitingForFeedback(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_ignore_feedback_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_published_datetime=ACTIVE_PERIOD_START)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_feedback)

    def test_ignore_deadline_not_expired_first_attempt(self):
        baker.make('core.AssignmentGroup',
                   parentnode__first_deadline=ACTIVE_PERIOD_END)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_feedback)

    def test_ignore_deadline_not_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_END)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_feedback)

    def test_include_deadline_expired_first_attempt(self):
        baker.make('core.AssignmentGroup',
                   parentnode__first_deadline=ACTIVE_PERIOD_START)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_feedback)

    def test_include_deadline_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_feedback)

    def test_include_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=10))
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_feedback)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup2 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup3 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup4 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup5 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_END)

        # Should be waiting for feedback
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup2,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=1))

        # Should not be waiting for feedback
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup3)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup4)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup4)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup5)

        annotated_groups = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count()
        self.assertTrue(annotated_groups.get(id=testgroup1.id).annotated_is_waiting_for_feedback)
        self.assertTrue(annotated_groups.get(id=testgroup2.id).annotated_is_waiting_for_feedback)
        self.assertFalse(annotated_groups.get(id=testgroup3.id).annotated_is_waiting_for_feedback)
        self.assertFalse(annotated_groups.get(id=testgroup4.id).annotated_is_waiting_for_feedback)
        self.assertFalse(annotated_groups.get(id=testgroup5.id).annotated_is_waiting_for_feedback)


class TestAssignmentGroupIsWaitingForDeliveries(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_feedback_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_deliveries)

    def test_false_deadline_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_deliveries)

    def test_false_deadline_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_waiting_for_deliveries)

    def test_true_deadline_not_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_END)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_deliveries)

    def test_true_deadline_not_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_END)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_deliveries)

    def test_true_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timedelta(days=1))
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_waiting_for_deliveries)


class TestAssignmentGroupQuerysetAnnotateWithIsWaitingForDeliveries(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_feedback_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_deliveries)

    def test_false_deadline_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_deliveries)

    def test_false_deadline_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_START)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertFalse(annotated_group.annotated_is_waiting_for_deliveries)

    def test_true_deadline_not_expired_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_END)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_deliveries)

    def test_true_deadline_not_expired_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=ACTIVE_PERIOD_END)
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_deliveries)

    def test_true_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__first_deadline=ACTIVE_PERIOD_START)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timedelta(days=1))
        annotated_group = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        self.assertTrue(annotated_group.annotated_is_waiting_for_deliveries)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_END)
        testgroup2 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup3 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup4 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup5 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)

        # Should be waiting for deliveries
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup2,
            deadline_datetime=ACTIVE_PERIOD_END)

        # Should not be waiting for deliveries
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup3)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup4)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup4)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup5)

        annotated_groups = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count()
        self.assertTrue(annotated_groups.get(id=testgroup1.id).annotated_is_waiting_for_deliveries)
        self.assertTrue(annotated_groups.get(id=testgroup2.id).annotated_is_waiting_for_deliveries)
        self.assertFalse(annotated_groups.get(id=testgroup3.id).annotated_is_waiting_for_deliveries)
        self.assertFalse(annotated_groups.get(id=testgroup4.id).annotated_is_waiting_for_deliveries)
        self.assertFalse(annotated_groups.get(id=testgroup5.id).annotated_is_waiting_for_deliveries)


class TestAssignmentGroupIsCorrected(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_feedback_not_published_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_corrected)

    def test_false_feedback_not_published_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_corrected)

    def test_true_feedback_is_published_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_corrected)

    def test_true_feedback_is_published_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_corrected)

    def test_false_multiple_feedbacksets_last_is_not_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.is_corrected)

    def test_true_multiple_feedbacksets_last_is_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.is_corrected)


class TestAssignmentGroupQuerySetAnnotateWithIsCorrected(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_feedback_not_published_first_attempt(self):
        baker.make('core.AssignmentGroup')
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertFalse(annotated_group.annotated_is_corrected)

    def test_false_feedback_not_published_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertFalse(annotated_group.annotated_is_corrected)

    def test_true_feedback_is_published_first_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertTrue(annotated_group.annotated_is_corrected)

    def test_true_feedback_is_published_new_attempt(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertTrue(annotated_group.annotated_is_corrected)

    def test_false_multiple_feedbacksets_last_is_not_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertFalse(annotated_group.annotated_is_corrected)

    def test_true_multiple_feedbacksets_last_is_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        self.assertTrue(annotated_group.annotated_is_corrected)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup2 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup3 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)
        testgroup4 = baker.make('core.AssignmentGroup',
                                parentnode__first_deadline=ACTIVE_PERIOD_START)

        # Should be corrected
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup2)

        # Should not be corrected
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup3)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup4)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup4)

        annotated_groups = AssignmentGroup.objects.annotate_with_is_corrected_count()
        self.assertTrue(annotated_groups.get(id=testgroup1.id).annotated_is_corrected)
        self.assertTrue(annotated_groups.get(id=testgroup2.id).annotated_is_corrected)
        self.assertFalse(annotated_groups.get(id=testgroup3.id).annotated_is_corrected)
        self.assertFalse(annotated_groups.get(id=testgroup4.id).annotated_is_corrected)


class TestAssignmentGroupPublishedGradingPoints(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_published_grading_points_not_published_none(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertEqual(None, testgroup.published_grading_points)

    def test_published_grading_points(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertEqual(10, testgroup.published_grading_points)

    def test_published_grading_points_zero_is_not_none(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=0)
        testgroup.refresh_from_db()
        self.assertEqual(0, testgroup.published_grading_points)

    def test_published_grading_points_multiple_last_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup,
            grading_points=20,
            deadline_datetime=timezone.now() + timedelta(days=3))
        testgroup.refresh_from_db()
        self.assertEqual(20, testgroup.published_grading_points)

    def test_published_grading_points_multiple_last_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            grading_points=20)
        testgroup.refresh_from_db()
        self.assertEqual(10, testgroup.published_grading_points)


class TestAssignmentGroupDraftedGradingPoints(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_drafted_grading_points_not_published_is_ok(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertEqual(10, testgroup.drafted_grading_points)

    def test_drafted_grading_points_zero_is_not_none(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup,
            grading_points=0)
        testgroup.refresh_from_db()
        self.assertEqual(0, testgroup.drafted_grading_points)

    def test_drafted_grading_points_published_same_as_last_is_none(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertEqual(None, testgroup.drafted_grading_points)

    def test_drafted_grading_points_multiple_last_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            grading_points=20)
        testgroup.refresh_from_db()
        self.assertEqual(20, testgroup.drafted_grading_points)


class TestAssignmentGroupPublishedGradeIsPassingGrade(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_published_grade_is_passing_grade_false_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.published_grade_is_passing_grade)

    def test_published_grade_is_passing_grade_false_published(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=9)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.published_grade_is_passing_grade)

    def test_published_grade_is_passing_grade_true(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.published_grade_is_passing_grade)

    def test_published_grade_is_passing_grade_multiple_last_published(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=5)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup,
            grading_points=15,
            deadline_datetime=timezone.now() + timedelta(days=3))
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.published_grade_is_passing_grade)

    def test_published_grade_is_passing_grade_multiple_last_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=5)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            grading_points=20)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.published_grade_is_passing_grade)


class TestAssignmentGroupQuerySetExtraAnnotateWithDatetimeOfLastAdminComment(TestCase):
    def test_extra_annotate_datetime_of_last_admin_comment(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        queryset = AssignmentGroup.objects.all().extra_annotate_datetime_of_last_admin_comment()
        self.assertEqual(default_timezone_datetime(2010, 12, 24, 0, 0),
                         queryset.first().datetime_of_last_admin_comment)

    def test_extra_annotate_datetime_of_last_admin_comment_ignore_private_comment(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        queryset = AssignmentGroup.objects.all().extra_annotate_datetime_of_last_admin_comment()
        self.assertEqual(None,
                         queryset.first().datetime_of_last_admin_comment)

    def test_extra_annotate_datetime_of_last_admin_comment_ignore_student_comment(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_STUDENT,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        queryset = AssignmentGroup.objects.all().extra_annotate_datetime_of_last_admin_comment()
        self.assertEqual(None,
                         queryset.first().datetime_of_last_admin_comment)

    def test_extra_annotate_datetime_of_last_admin_comment_ignore_examiner_comment(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        queryset = AssignmentGroup.objects.all().extra_annotate_datetime_of_last_admin_comment()
        self.assertEqual(None,
                         queryset.first().datetime_of_last_admin_comment)

    def test_extra_annotate_datetime_of_last_admin_comment_ordering(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2009, 12, 24, 0, 0))
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2011, 12, 24, 0, 0))
        queryset = AssignmentGroup.objects.all().extra_annotate_datetime_of_last_admin_comment()
        self.assertEqual(default_timezone_datetime(2011, 12, 24, 0, 0),
                         queryset.first().datetime_of_last_admin_comment)


class TestAssignmentGroupQuerySetExtraOrderByDatetimeOfLastAdminComment(TestCase):
    def test_extra_order_by_datetime_of_last_admin_comment_ascending(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2011, 12, 24, 0, 0))
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup2,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2012, 12, 24, 0, 0))
        testgroup3 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup3,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        groups = list(AssignmentGroup.objects.all().extra_order_by_datetime_of_last_admin_comment())
        self.assertEqual(testgroup3, groups[0])
        self.assertEqual(testgroup1, groups[1])
        self.assertEqual(testgroup2, groups[2])

    def test_extra_order_by_datetime_of_last_admin_comment_no_admin_comment_last(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2010, 12, 24, 0, 0))
        testgroup2 = baker.make('core.AssignmentGroup')
        testgroup3 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup3,
                   user_role=Comment.USER_ROLE_ADMIN,
                   published_datetime=default_timezone_datetime(2012, 12, 24, 0, 0))
        groups = list(AssignmentGroup.objects.all().extra_order_by_datetime_of_last_admin_comment())
        self.assertEqual(testgroup1, groups[0])
        self.assertEqual(testgroup3, groups[1])
        self.assertEqual(testgroup2, groups[2])  # No admin comment makes this come last


class TestAssignmentGroupQuerySetFilterUserIsAdmin(TestCase):
    def test_filter_user_is_admin_is_not_admin_on_anything(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.AssignmentGroup')
        self.assertFalse(AssignmentGroup.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin_superuser(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testgroup = baker.make('core.AssignmentGroup')
        self.assertEqual(
            {testgroup},
            set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_ignore_assignments_where_not_in_group(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.AssignmentGroup')
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testgroup.period)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode=testperiod)
        testassignment2 = baker.make('core.Assignment',
                                     parentnode=testperiod)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1, testgroup2},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period_ignore_semi_anonymous(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode=testperiod)
        testassignment2 = baker.make(
            'core.Assignment',
            parentnode=testperiod,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        baker.make('core.AssignmentGroup', parentnode=testassignment2)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period_ignore_fully_anonymous(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode=testperiod)
        testassignment2 = baker.make(
            'core.Assignment',
            parentnode=testperiod,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        baker.make('core.AssignmentGroup', parentnode=testassignment2)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = baker.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1, testgroup2},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject_include_semi_anonymous(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = baker.make(
            'core.Assignment',
            parentnode__parentnode=testsubject,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1, testgroup2},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject_include_fully_anonymous(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testassignment1 = baker.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = baker.make(
            'core.Assignment',
            parentnode__parentnode=testsubject,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
                {testgroup1, testgroup2},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_distinct(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testperiod = baker.make('core.Period', parentnode=testsubject)
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        subjectpermissiongroup1 = baker.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        subjectpermissiongroup2 = baker.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup1.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup2.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup1.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup2.permissiongroup)
        self.assertEqual(
                {testgroup},
                set(AssignmentGroup.objects.filter_user_is_admin(user=testuser)))


class TestAssignmentGroupQuerySetAnnotateWithNumberOfPublishedFeedbacksets(TestCase):
    def test_annotate_with_number_of_published_feedbacksets_zero(self):
        baker.make('core.AssignmentGroup')
        self.assertEqual(
            0,
            AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()
            .first().number_of_published_feedbacksets)

    def test_annotate_with_number_of_published_feedbacksets_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None)
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now())
        self.assertEqual(
            3,
            AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()
            .first().number_of_published_feedbacksets)

    def test_annotate_with_number_of_published_feedbacksets_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        testgroup2 = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup1,
                   grading_published_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup1,
                   grading_published_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup2,
                   grading_published_datetime=None)
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup2,
                   grading_published_datetime=timezone.now())
        queryset = AssignmentGroup.objects.annotate_with_number_of_published_feedbacksets()\
            .order_by('number_of_published_feedbacksets')
        self.assertEqual(testgroup2, queryset[0])
        self.assertEqual(1, queryset[0].number_of_published_feedbacksets)
        self.assertEqual(testgroup1, queryset[1])
        self.assertEqual(2, queryset[1].number_of_published_feedbacksets)


class TestAssignmentGroupQuerySetFilterWithPublishedFeedbackOrComments(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_filter_with_published_feedback_or_comments(self):
        testgroup_with_published_feedback = baker.make('core.AssignmentGroup')
        testgroup_with_unpublished_feedback = baker.make('core.AssignmentGroup')
        testgroup_with_groupcomment = baker.make('core.AssignmentGroup')
        testgroup_with_imageannotationcomment = baker.make('core.AssignmentGroup')
        baker.make('core.AssignmentGroup')
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup_with_published_feedback,
                   deadline_datetime=timezone.now(),
                   grading_published_datetime=timezone.now())
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup_with_unpublished_feedback,
                   deadline_datetime=timezone.now(),
                   grading_published_datetime=None)
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup_with_groupcomment,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set__group=testgroup_with_imageannotationcomment,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION)
        queryset = AssignmentGroup.objects.filter_with_published_feedback_or_comments()
        self.assertEqual(
            {testgroup_with_published_feedback,
             testgroup_with_groupcomment,
             testgroup_with_imageannotationcomment},
            set(queryset))


class TestAssignmentGroupHasUnpublishedFeedbackset(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_feedbackset(self):
        testgroup = baker.make('core.AssignmentGroup')
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.has_unpublished_feedbackdraft)

    def test_false_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.has_unpublished_feedbackdraft)

    def test_false_no_grading_points(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testgroup.refresh_from_db()
        self.assertFalse(testgroup.has_unpublished_feedbackdraft)

    def test_true(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup, grading_points=1)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.has_unpublished_feedbackdraft)

    def test_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup, grading_points=1)
        testgroup.refresh_from_db()
        self.assertTrue(testgroup.has_unpublished_feedbackdraft)


class TestAssignmentGroupAnnotateWithHasUnpublishedFeedbackset(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_feedbackset(self):
        testgroup = baker.make('core.AssignmentGroup')
        annotated_group = AssignmentGroup.objects.annotate_with_has_unpublished_feedbackdraft_count().first()
        self.assertFalse(annotated_group.annotated_has_unpublished_feedbackdraft)

    def test_false_published(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_has_unpublished_feedbackdraft_count().first()
        self.assertFalse(annotated_group.annotated_has_unpublished_feedbackdraft)

    def test_false_no_grading_points(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        annotated_group = AssignmentGroup.objects.annotate_with_has_unpublished_feedbackdraft_count().first()
        self.assertFalse(annotated_group.annotated_has_unpublished_feedbackdraft)

    def test_true(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup, grading_points=1)
        annotated_group = AssignmentGroup.objects.annotate_with_has_unpublished_feedbackdraft_count().first()
        self.assertTrue(annotated_group.annotated_has_unpublished_feedbackdraft)

    def test_multiple_feedbacksets(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup, grading_points=1)
        annotated_group = AssignmentGroup.objects.annotate_with_has_unpublished_feedbackdraft_count().first()
        self.assertTrue(annotated_group.annotated_has_unpublished_feedbackdraft)


class TestAssignmentGroupQuerySetPrefetchAssignmentWithPointsToGradeMap(TestCase):
    def test_no_pointtogrademap(self):
        testgroup = baker.make('core.AssignmentGroup')
        annotated_group = AssignmentGroup.objects\
            .prefetch_assignment_with_points_to_grade_map().get(id=testgroup.id)
        self.assertIsNone(annotated_group.prefetched_assignment.prefetched_point_to_grade_map)

    def test_has_pointtogrademap(self):
        testgroup = baker.make('core.AssignmentGroup')
        point_to_grade_map = baker.make('core.PointToGradeMap', assignment=testgroup.assignment)
        annotated_group = AssignmentGroup.objects\
            .prefetch_assignment_with_points_to_grade_map().get(id=testgroup.id)
        self.assertEqual(point_to_grade_map,
                         annotated_group.prefetched_assignment.prefetched_point_to_grade_map)


class TestAssignmentGroupQuerySetAnnotateWithNumberOfPrivateGroupcommentsFromUser(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_zero(self):
        baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        queryset = AssignmentGroup.objects.annotate_with_number_of_private_groupcomments_from_user(
            user=testuser)
        self.assertEqual(0, queryset.first().number_of_private_groupcomments_from_user)

    def test_only_private(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        annotated_group = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser).first()
        self.assertEqual(1, annotated_group.number_of_private_groupcomments_from_user)

    def test_only_from_user(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        annotated_group = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser).first()
        self.assertEqual(2, annotated_group.number_of_private_groupcomments_from_user)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset1 = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup1)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)

        testgroup2 = baker.make('core.AssignmentGroup')
        feedbackset2 = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset2,
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)

        queryset = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser)
        self.assertEqual(
            2,
            queryset.get(id=testgroup1.id).number_of_private_groupcomments_from_user)
        self.assertEqual(
            1,
            queryset.get(id=testgroup2.id).number_of_private_groupcomments_from_user)


class TestAssignmentGroupQuerySetAnnotateWithNumberOfPrivateImageannotationcommentsFromUser(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_zero(self):
        baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        queryset = AssignmentGroup.objects.annotate_with_number_of_private_imageannotationcomments_from_user(
            user=testuser)
        self.assertEqual(0, queryset.first().number_of_private_imageannotationcomments_from_user)

    def test_only_private(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        annotated_group = AssignmentGroup.objects\
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=testuser).first()
        self.assertEqual(1, annotated_group.number_of_private_imageannotationcomments_from_user)

    def test_only_from_user(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        annotated_group = AssignmentGroup.objects\
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=testuser).first()
        self.assertEqual(2, annotated_group.number_of_private_imageannotationcomments_from_user)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        feedbackset1 = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup1)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)

        testgroup2 = baker.make('core.AssignmentGroup')
        feedbackset2 = devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        baker.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset2,
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)

        queryset = AssignmentGroup.objects\
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=testuser)
        self.assertEqual(
            2,
            queryset.get(id=testgroup1.id).number_of_private_imageannotationcomments_from_user)
        self.assertEqual(
            1,
            queryset.get(id=testgroup2.id).number_of_private_imageannotationcomments_from_user)


class TestAssignmentGroupQuerySetAnnotateWithIsPassingGrade(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_false_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup,
            grading_points=10)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertFalse(queryset.first().is_passing_grade)

    def test_false_published(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=9)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertFalse(queryset.first().is_passing_grade)

    def test_true(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=20)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertTrue(queryset.first().is_passing_grade)

    def test_true_gte(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertTrue(queryset.first().is_passing_grade)

    def test_multiple_last_published(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=5)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup,
            grading_points=15,
            deadline_datetime=timezone.now() + timedelta(days=3))
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertTrue(queryset.first().is_passing_grade)

    def test_multiple_last_unpublished(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__passing_grade_min_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=5)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            grading_points=20)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertFalse(queryset.first().is_passing_grade)

    def test_multiple_groups(self):
        testgroup1 = baker.make('core.AssignmentGroup',
                                parentnode__passing_grade_min_points=10)
        testgroup2 = baker.make('core.AssignmentGroup',
                                parentnode__passing_grade_min_points=30)
        testgroup3 = baker.make('core.AssignmentGroup',
                                parentnode__passing_grade_min_points=20)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup1,
            grading_points=10)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup2,
            grading_points=20)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup3,
            grading_points=30)
        queryset = AssignmentGroup.objects.all().annotate_with_is_passing_grade_count()
        self.assertTrue(queryset.get(id=testgroup1.id).is_passing_grade)
        self.assertFalse(queryset.get(id=testgroup2.id).is_passing_grade)
        self.assertTrue(queryset.get(id=testgroup3.id).is_passing_grade)
