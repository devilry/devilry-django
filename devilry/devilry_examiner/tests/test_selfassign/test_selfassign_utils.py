from django import test
from django.conf import settings
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql

from devilry.devilry_examiner.views.selfassign import utils


class TestGroupsAvailableForSelfAssign(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_user_not_relatedexaminer_on_period(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)

    def test_selfassign_disabled(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=False
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)

    def test_limit_zero(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True,
            examiner_self_assign_limit=0
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)

    def test_selfassign_limit_reached(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', assignmentgroup=group)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)

    def test_selfassign_available_assignment_semi_anonymized_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)
    
    def test_selfassign_available_assignment_fully_anonymized_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True,
            anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 0)

    def test_selfassign_available_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 1)

    def test_selfassign_available_limit_reached_but_user_is_examiner(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        related_examiner = baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', 
            assignmentgroup=group,
            relatedexaminer=related_examiner)
        groupqueryset = utils.assignment_groups_available_for_self_assign(
            period=assignment.parentnode, user=examiner_user)
        self.assertEqual(groupqueryset.count(), 1)


class TestSelfAssignAvailablePeriods(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_user_not_related_examiner_on_period_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.AssignmentGroup', parentnode=assignment)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 0)
    
    def test_period_not_active_ended(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 0)

    def test_period_not_active_not_started(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 0)
    
    def test_single_period_accessible_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 1)
    
    def test_multiple_periods_accessible_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment Two',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment1.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment1)
        baker.make('core.RelatedExaminer', period=assignment2.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment2)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 2)
        self.assertIn(assignment1.period, periodqueryset)
        self.assertIn(assignment2.period, periodqueryset)

    def test_period_accessible_user_already_examiner(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        relatedexaminer = baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', assignmentgroup=group, relatedexaminer=relatedexaminer)
        periodqueryset = utils.selfassign_available_periods(user=examiner_user)
        self.assertEqual(periodqueryset.count(), 1)
