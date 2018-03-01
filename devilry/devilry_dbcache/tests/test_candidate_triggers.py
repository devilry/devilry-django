from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.apps.core.models import Candidate, CandidateAssignmentGroupHistory
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestCandidateTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_insert_history_model_is_created_when_candidate_is_created(self):
        mommy.make('core.Candidate')
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 1)

    def test_insert_history_models_created_fields(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user=testuser)
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 1)
        history = CandidateAssignmentGroupHistory.objects.get()
        self.assertEqual(history.assignment_group, testgroup)
        self.assertEqual(history.user, testuser)
        self.assertTrue(history.is_add)

    def test_insert_history_models_fields_multiple(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        testuser1 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user=testuser1)

        testgroup2 = mommy.make('core.AssignmentGroup')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user=testuser2)

        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 2)

        history1 = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup1.id)
        history2 = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup2.id)

        self.assertEqual(history1.assignment_group, testgroup1)
        self.assertEqual(history1.user, testuser1)
        self.assertTrue(history1.is_add)

        self.assertEqual(history2.assignment_group, testgroup2)
        self.assertEqual(history2.user, testuser2)
        self.assertTrue(history2.is_add)

    def test_delete_history_model_is_created_when_candidate_is_created(self):
        mommy.make('core.Candidate')
        Candidate.objects.get().delete()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 2)

    def test_delete_history_models_created_fields(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user=testuser)
        Candidate.objects.get().delete()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 2)

        history_created = CandidateAssignmentGroupHistory.objects.filter(is_add=True).get()
        self.assertEqual(history_created.assignment_group, testgroup)
        self.assertEqual(history_created.user, testuser)
        self.assertTrue(history_created.is_add)

        history_deleted = CandidateAssignmentGroupHistory.objects.filter(is_add=False).get()
        self.assertEqual(history_deleted.assignment_group, testgroup)
        self.assertEqual(history_deleted.user, testuser)
        self.assertFalse(history_deleted.is_add)

    def test_delete_history_models_fields_multiple(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        testuser1 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user=testuser1)

        testgroup2 = mommy.make('core.AssignmentGroup')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user=testuser2)
        Candidate.objects.all().delete()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 4)

        # Test history1 create/delete history entries.
        history1_created = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup1.id, is_add=True)
        history1_deleted = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup1.id, is_add=False)

        self.assertEqual(history1_created.assignment_group, testgroup1)
        self.assertEqual(history1_created.user, testuser1)
        self.assertTrue(history1_created.is_add)

        self.assertEqual(history1_deleted.assignment_group, testgroup1)
        self.assertEqual(history1_deleted.user, testuser1)
        self.assertFalse(history1_deleted.is_add)

        # Test history2 create/delete history entries.
        history2_created = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup2.id, is_add=True)
        history2_deleted = CandidateAssignmentGroupHistory.objects.get(assignment_group_id=testgroup2.id, is_add=False)
        self.assertEqual(history2_created.assignment_group, testgroup2)
        self.assertEqual(history2_created.user, testuser2)
        self.assertTrue(history2_created.is_add)

        self.assertEqual(history2_deleted.assignment_group, testgroup2)
        self.assertEqual(history2_deleted.user, testuser2)
        self.assertFalse(history2_deleted.is_add)

    def test_update_candidate_assignment_group_is_changed(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testgroup_updated_to = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        candidate.assignment_group = testgroup_updated_to
        candidate.save()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 3)

        history_entry_from_group = CandidateAssignmentGroupHistory.objects.get(
            assignment_group_id=testgroup.id, is_add=False)
        self.assertEqual(history_entry_from_group.user, testuser)

        history_entry_to_group = CandidateAssignmentGroupHistory.objects.get(
            assignment_group_id=testgroup_updated_to.id, is_add=True)
        self.assertEqual(history_entry_to_group.user, testuser)

    def test_update_candidate_assignment_group_multiple_changes(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        testgroup2 = mommy.make('core.AssignmentGroup')
        testgroup3 = mommy.make('core.AssignmentGroup')
        testgroup4 = mommy.make('core.AssignmentGroup')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup1, relatedcandidate__user=testuser)
        candidate.assignment_group = testgroup2
        candidate.save()
        candidate.assignment_group = testgroup3
        candidate.save()
        candidate.assignment_group = testgroup4
        candidate.save()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 7)

    def test_assignment_group_is_deleted_ok(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup)
        testgroup.delete()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 0)

    def test_relatedstudent_is_deleted_ok(self):
        testgroup = mommy.make('core.AssignmentGroup')
        relatedstudent = mommy.make('core.RelatedStudent')
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        relatedstudent.delete()
        self.assertEqual(CandidateAssignmentGroupHistory.objects.count(), 2)
