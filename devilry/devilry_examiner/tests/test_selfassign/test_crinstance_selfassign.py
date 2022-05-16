import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql

from devilry.devilry_examiner.views.selfassign import crinstance_selfassign


class TestCradminInstanceAssignment(test.TestCase):
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
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 0)
    
    def test_period_not_active_ended(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 0)

    def test_period_not_active_not_started(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 0)
    
    def test_single_period_accessible_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 1)
    
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
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 2)
        self.assertIn(assignment1.period, crinstance.get_rolequeryset())
        self.assertIn(assignment2.period, crinstance.get_rolequeryset())

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
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner_user
        crinstance = crinstance_selfassign.CrAdminInstance(request=mockrequest)
        self.assertEqual(crinstance.get_rolequeryset().count(), 1)
