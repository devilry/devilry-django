from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from mock import patch
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Q
from model_mommy import mommy
from devilry.apps.core.models.assignment import AssignmentHasGroupsError
from devilry.devilry_group.models import FeedbackSet

from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.apps.core.models import Period, Examiner, AssignmentGroup, RelatedStudent
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import PointToGradeMap
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface
from ..testhelper import TestHelper


class TestAssignment(TestCase):

    def test_points_is_passing_grade(self):
        assignment1 = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', passing_grade_min_points=1).assignment
        self.assertTrue(assignment1.points_is_passing_grade(1))
        self.assertFalse(assignment1.points_is_passing_grade(0))

    def test_points_to_grade_passed_failed(self):
        assignment1 = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', points_to_grade_mapper='passed-failed').assignment
        self.assertEquals(assignment1.points_to_grade(0), 'failed')
        self.assertEquals(assignment1.points_to_grade(1), 'passed')

    def test_points_to_grade_points(self):
        assignment1 = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment(
                'assignment1',
                points_to_grade_mapper='raw-points',
                max_points=10).assignment
        self.assertEquals(assignment1.points_to_grade(0), '0/10')
        self.assertEquals(assignment1.points_to_grade(1), '1/10')
        self.assertEquals(assignment1.points_to_grade(10), '10/10')

    def test_points_to_grade_custom_table(self):
        assignment1 = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment(
                'assignment1',
                points_to_grade_mapper='custom-table',
                max_points=10).assignment
        pointtogrademap = PointToGradeMap.objects.create(
            assignment=assignment1)
        pointtogrademap.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=10,
            grade='Ok'
        )
        pointtogrademap.clean()
        pointtogrademap.save()
        self.assertEquals(assignment1.points_to_grade(5), 'Ok')

    def test_has_valid_grading_setup_valid_by_default(self):
        assignment1 = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1').assignment

        # Mock the gradingsystempluginregistry
        myregistry = GradingSystemPluginRegistry()

        class MockApprovedPluginApi(GradingSystemPluginInterface):
            id = 'devilry_gradingsystemplugin_approved'
        myregistry.add(MockApprovedPluginApi)

        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            self.assertTrue(assignment1.has_valid_grading_setup())

    def test_set_max_points(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment(
                'assignment1',
                points_to_grade_mapper='custom-table',
                max_points=10)
        PointToGradeMap.objects.create(
            invalid=False,
            assignment=assignmentbuilder.assignment)
        assignmentbuilder.assignment.set_max_points(20)
        assignmentbuilder.assignment.save()
        assignmentbuilder.reload_from_db()
        self.assertEquals(assignmentbuilder.assignment.max_points, 20)
        self.assertTrue(assignmentbuilder.assignment.pointtogrademap.invalid)

    def test_feedback_workflow_allows_shared_feedback_drafts_default(self):
        testassignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            feedback_workflow='').assignment
        self.assertFalse(testassignment.feedback_workflow_allows_shared_feedback_drafts())

    def test_feedback_workflow_allows_shared_feedback_drafts_trusted_cooperative_feedback_editing(self):
        testassignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            feedback_workflow='trusted-cooperative-feedback-editing').assignment
        self.assertTrue(testassignment.feedback_workflow_allows_shared_feedback_drafts())

    def test_feedback_workflow_allows_examiners_publish_feedback_default(self):
        testassignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            feedback_workflow='').assignment
        self.assertTrue(testassignment.feedback_workflow_allows_examiners_publish_feedback())

    def test_feedback_workflow_allows_examiners_publish_feedback_trusted_cooperative_feedback_editing(self):
        testassignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                            feedback_workflow='trusted-cooperative-feedback-editing').assignment
        self.assertFalse(testassignment.feedback_workflow_allows_examiners_publish_feedback())

    def test_copy_groups_from_another_assignment_source_has_no_groups(self):
        sourceassignment = mommy.make('core.Assignment')
        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 0)

    def test_copy_groups_from_another_assignment_target_has_groups(self):
        sourceassignment = mommy.make('core.Assignment')
        targetassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=targetassignment)
        with self.assertRaises(AssignmentHasGroupsError):
            targetassignment.copy_groups_from_another_assignment(sourceassignment)

    def test_copy_groups_from_another_assignment_groups_is_created(self):
        sourceassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=sourceassignment, _quantity=5)
        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 5)

    def test_copy_groups_from_another_assignment_candidates(self):
        sourceassignment = mommy.make('core.Assignment')
        student1 = mommy.make(settings.AUTH_USER_MODEL, shortname='student1')
        student2 = mommy.make(settings.AUTH_USER_MODEL, shortname='student2')
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   relatedstudent__user=student1)
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   relatedstudent__user=student2)

        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 2)
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=targetassignment)
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student2').exists())

    def test_copy_groups_from_another_assignment_querycount(self):
        sourceassignment = mommy.make('core.Assignment')
        group1 = mommy.make('core.AssignmentGroup', parentnode=sourceassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=sourceassignment)
        mommy.make('core.Candidate', assignment_group=group1, _quantity=40)
        mommy.make('core.Examiner', assignmentgroup=group1, _quantity=20)
        mommy.make('core.Candidate', assignment_group=group2, _quantity=5)
        mommy.make('core.Examiner', assignmentgroup=group2, _quantity=2)

        targetassignment = mommy.make('core.Assignment')
        # Should require only 9 queries no matter how many groups, candidates or examiners we
        # have (at least up to the max number of bulk created object per query):
        # 1. Check if any groups exists within the targetassignment.
        # 2. Query for all groups within the sourceassignment.
        # 3. Bulk create groups (without any candidates or examiners)
        # 4. Query for all the newly bulk created groups.
        # 5. Prefetch the source groups (via copied_from).
        # 6. Prefetch related candidates on the targetassignment (via copied_from).
        # 7. Prefetch related examiners on the targetassignment (via copied_from).
        # 8. Bulk create candidates.
        # 9. Bulk create examiners.
        with self.assertNumQueries(9):
            targetassignment.copy_groups_from_another_assignment(sourceassignment)

    def test_create_groups_from_relatedstudents_on_period_period_has_no_relatedstudents(self):
        testassignment = mommy.make('core.Assignment')
        testassignment.create_groups_from_relatedstudents_on_period()
        self.assertEqual(testassignment.assignmentgroups.count(), 0)

    def test_create_groups_from_relatedstudents_on_period_assignment_has_groups(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(AssignmentHasGroupsError):
            testassignment.create_groups_from_relatedstudents_on_period()

    def test_create_groups_from_relatedstudents_on_period_groups_is_created(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=5)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment.create_groups_from_relatedstudents_on_period()
        self.assertEqual(testassignment.assignmentgroups.count(), 5)

    def test_create_groups_from_relatedstudents_on_period_candidates_is_created(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=5)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment.create_groups_from_relatedstudents_on_period()
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=testassignment)
        self.assertEqual(candidatesqueryset.count(), 5)

    def test_create_groups_from_relatedstudents_on_period_candidates_has_correct_user(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, user__shortname='student1')
        mommy.make('core.RelatedStudent', period=testperiod, user__shortname='student2')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment.create_groups_from_relatedstudents_on_period()
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=testassignment)
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student2').exists())

    def test_create_groups_from_relatedstudents_on_period_querycount(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=30)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        # Should require only 5 queries no matter how many relatedstudents we
        # have (at least up to the max number of bulk created object per query):
        # 1. Check if any groups exists within the assignment.
        # 2. Query for all relatedstudents within the period.
        # 3. Bulk create empty groups.
        # 4. Query for all the created empty groups.
        # 5. Bulk create candidates.
        with self.assertNumQueries(5):
            testassignment.create_groups_from_relatedstudents_on_period()

    def test_setup_examiners_by_relateduser_syncsystem_tags_no_relatedstudents(self):
        testassignment = mommy.make('core.Assignment')
        testassignment.setup_examiners_by_relateduser_syncsystem_tags()

    def test_setup_examiners_by_relateduser_syncsystem_tags_simple(self):
        testperiod = mommy.make('core.Period')

        examiner1 = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner1')
        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   relatedexaminer__user=examiner1,
                   tag='group1')

        student1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                     user=student1,
                                     period=testperiod)
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent=relatedstudent1,
                   tag='group1')

        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=group1,
                   relatedstudent=relatedstudent1)

        testassignment.setup_examiners_by_relateduser_syncsystem_tags()
        self.assertEqual(group1.examiners.count(), 1)
        self.assertTrue(group1.examiners.filter(relatedexaminer__user__shortname='examiner1').exists())

    def test_setup_examiners_by_relateduser_syncsystem_tags_exclude_existing_examinerobjects(self):
        testperiod = mommy.make('core.Period')

        examiner1 = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner1')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', user=examiner1)
        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   relatedexaminer=relatedexaminer1,
                   tag='group1')

        student1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                     user=student1,
                                     period=testperiod)
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent=relatedstudent1,
                   tag='group1')

        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=group1,
                   relatedstudent=relatedstudent1)
        mommy.make('core.Examiner', assignmentgroup=group1,
                   relatedexaminer=relatedexaminer1)

        # NOTE: The real test here is that we do not get an IntegrityError
        self.assertEqual(group1.examiners.count(), 1)
        testassignment.setup_examiners_by_relateduser_syncsystem_tags()
        group1 = AssignmentGroup.objects.get(id=group1.id)
        self.assertEqual(group1.examiners.count(), 1)
        self.assertTrue(group1.examiners.filter(relatedexaminer__user__shortname='examiner1').exists())

    def test_setup_examiners_by_relateduser_syncsystem_tags_multiple_tags_and_examiners(self):
        testperiod = mommy.make('core.Period')

        examiner1 = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner1')
        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   relatedexaminer__user=examiner1,
                   tag='group1')
        examiner2 = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner2')
        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   relatedexaminer__user=examiner2,
                   tag='group2')

        student1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                     user=student1,
                                     period=testperiod)
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent=relatedstudent1,
                   tag='group1')
        student2 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent2 = mommy.make('core.RelatedStudent',
                                     user=student2,
                                     period=testperiod)
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent=relatedstudent2,
                   tag='group1')
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent=relatedstudent2,
                   tag='group2')

        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=group1,
                   relatedstudent=relatedstudent1)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=group2,
                   relatedstudent=relatedstudent2)

        testassignment.setup_examiners_by_relateduser_syncsystem_tags()
        self.assertEqual(Examiner.objects.count(), 3)
        self.assertEqual(group1.examiners.count(), 1)
        self.assertTrue(group1.examiners.filter(relatedexaminer__user__shortname='examiner1').exists())
        self.assertFalse(group1.examiners.filter(relatedexaminer__user__shortname='examiner2').exists())
        self.assertEqual(group2.examiners.count(), 2)
        self.assertTrue(group2.examiners.filter(relatedexaminer__user__shortname='examiner1').exists())
        self.assertTrue(group2.examiners.filter(relatedexaminer__user__shortname='examiner2').exists())

    def test_setup_examiners_by_relateduser_syncsystem_tags_querycount_minimal(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)

        # Should require 2 queries if we have no RelatedExaminerSyncSystemTags
        # 1. Map groupids to examiner user ID.
        # 2. Query for RelatedExaminerSyncSystemTag
        with self.assertNumQueries(2):
            testassignment.setup_examiners_by_relateduser_syncsystem_tags()

    def test_setup_examiners_by_relateduser_syncsystem_tags_querycount(self):
        testperiod = mommy.make('core.Period')

        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   tag='group1', _quantity=8)
        mommy.make('core.RelatedExaminerSyncSystemTag',
                   relatedexaminer__period=testperiod,
                   tag='group2', _quantity=10)

        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent__period=testperiod,
                   tag='group1', _quantity=20)
        mommy.make('core.RelatedStudentSyncSystemTag',
                   relatedstudent__period=testperiod,
                   tag='group2', _quantity=30)

        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        for relatedstudent in testperiod.relatedstudent_set.all():
            mommy.make('core.Candidate',
                       relatedstudent=relatedstudent,
                       assignment_group__parentnode=testassignment)

        # Should require 39 queries:
        # - 1 query to map groupids to examiner user ID.
        # - 1 query for RelatedExaminerSyncSystemTag
        # - 18 queries to get the RelatedStudentSyncSystemTag objects matching
        #       each of the 18 RelatedExaminerSyncSystemTag objects.
        # - 18 queries to get candidates for the relatedstudents.
        # - 1 query to bulk create the examiners
        with self.assertNumQueries(39):
            testassignment.setup_examiners_by_relateduser_syncsystem_tags()
        self.assertEqual(460, Examiner.objects.count())

    def test_students_must_be_anonymized_for_devilryrole_student_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_students_must_be_anonymized_for_devilryrole_student_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_students_must_be_anonymized_for_devilryrole_student_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_students_must_be_anonymized_for_devilryrole_examiner_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_students_must_be_anonymized_for_devilryrole_examiner_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertTrue(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_students_must_be_anonymized_for_devilryrole_examiner_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_students_must_be_anonymized_for_devilryrole_periodadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_students_must_be_anonymized_for_devilryrole_periodadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertTrue(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_students_must_be_anonymized_for_devilryrole_periodadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_students_must_be_anonymized_for_devilryrole_subjectadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_students_must_be_anonymized_for_devilryrole_subjectadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_students_must_be_anonymized_for_devilryrole_subjectadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_students_must_be_anonymized_for_devilryrole_departmentadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))

    def test_students_must_be_anonymized_for_devilryrole_departmentadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))

    def test_students_must_be_anonymized_for_devilryrole_departmentadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertFalse(assignment.students_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_student_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_examiners_must_be_anonymized_for_devilryrole_student_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertTrue(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_examiners_must_be_anonymized_for_devilryrole_student_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='student'))

    def test_examiners_must_be_anonymized_for_devilryrole_examiner_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_examiners_must_be_anonymized_for_devilryrole_examiner_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_examiners_must_be_anonymized_for_devilryrole_examiner_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='examiner'))

    def test_examiners_must_be_anonymized_for_devilryrole_periodadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_periodadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertTrue(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_periodadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='periodadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_subjectadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_subjectadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_subjectadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertTrue(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='subjectadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_departmentadmin_nonanonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_departmentadmin_semi_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))

    def test_examiners_must_be_anonymized_for_devilryrole_departmentadmin_fully_anonymous_assignment(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.assertFalse(assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole='departmentadmin'))


class TestAssignmentQuerySet(TestCase):
    def test_filter_is_active(self):
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        activeassignmentbuilder = duck1010builder.add_6month_active_period().add_assignment('week1')

        # Add inactive groups to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1')
        duck1010builder.add_6month_nextyear_period().add_assignment('week1')

        qry = Assignment.objects.filter_is_active()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], activeassignmentbuilder.assignment)

    def test_filter_user_is_examiner(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make('core.Assignment')
        assignmentgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedexaminer = mommy.make('core.RelatedExaminer', user=user)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=assignmentgroup)
        queryset = Assignment.objects.filter_user_is_examiner(user)
        self.assertEquals(queryset.count(), 1)
        returned_assignment = queryset.first()
        self.assertTrue(assignment.id, returned_assignment.id)

    def test_filter_user_is_examiner_active_is_false_hence_user_is_not_examiner(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make('core.Assignment')
        assignmentgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedexaminer = mommy.make('core.RelatedExaminer', user=user, active=False)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer,
                   assignmentgroup=assignmentgroup)
        queryset = Assignment.objects.filter_user_is_examiner(user)
        self.assertEquals(queryset.count(), 0)

    def test_filter_user_is_candidate(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make('core.Assignment')
        mommy.make(
                'core.Candidate',
                relatedstudent=mommy.make('core.RelatedStudent', user=user),
                assignment_group=mommy.make('core.AssignmentGroup', parentnode=assignment))
        queryset = Assignment.objects.filter_student_has_access(user)
        self.assertEquals(queryset.count(), 1)
        returned_assignment = queryset.first()
        self.assertTrue(assignment.id, returned_assignment.id)

    def test_filter_user_is_not_candidate(self):
        user_not_set_as_candidate = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make('core.Assignment')
        mommy.make(
                'core.Candidate',
                relatedstudent=mommy.make(
                        'core.RelatedStudent',
                        user=mommy.make(settings.AUTH_USER_MODEL)),
                assignment_group=mommy.make(
                        'core.AssignmentGroup',
                        parentnode=assignment))
        queryset = Assignment.objects.filter_student_has_access(user_not_set_as_candidate)
        self.assertEquals(queryset.count(), 0)


class TestAssignmentQuerySetAnnotateWithWaitingForFeedback(TestCase):
    def test_annotate_with_waiting_for_feedback_count_nomatch_deadline_not_expired(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group__parentnode__first_deadline=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() + timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_deadline_not_expired_first_feedbackset(self):
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode__first_deadline=timezone.now() + timedelta(days=1),
                   grading_published_datetime=None,
                   deadline_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_is_not_last_in_group(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group__parentnode__first_deadline=timezone.now() - timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=None)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_grading_published(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   group__parentnode__first_deadline=timezone.now() - timedelta(days=2),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_in_same_group(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=4))
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(1, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_groups(self):
        testassignment = mommy.make('core.Assignment',
                                    first_deadline=timezone.now() - timedelta(days=4))
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=True)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=None,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(2, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_assignments(self):
        testassignment1 = mommy.make('core.Assignment',
                                     first_deadline=timezone.now() - timedelta(days=10))
        testassignment2 = mommy.make('core.Assignment',
                                     first_deadline=timezone.now() - timedelta(days=4))
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment1,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment1,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment2,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment2,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(2, queryset.count())
        self.assertEqual(1, queryset.get(pk=testassignment1.pk).waiting_for_feedback_count)
        self.assertEqual(2, queryset.get(pk=testassignment2.pk).waiting_for_feedback_count)


class TestAssignmentQuerySetFilterIsAdmin(TestCase):
    def test_filter_user_is_admin_is_not_admin_on_anything(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Assignment')
        self.assertFalse(Assignment.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin_superuser(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = mommy.make('core.Assignment')
        self.assertEqual(
            {testassignment},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_ignore_assignments_where_not_in_group(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.Assignment')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testassignment},
                set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make('core.Assignment')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment',
                                     parentnode=testperiod)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1, testassignment2},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period_ignore_semi_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode=testperiod)
        mommy.make('core.Assignment',
                   parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_period_ignore_fully_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode=testperiod)
        mommy.make('core.Assignment',
                   parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1, testassignment2},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject_ignore_semi_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject,
                                     anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1, testassignment2},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject_ignore_fully_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testassignment1 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject)
        testassignment2 = mommy.make('core.Assignment',
                                     parentnode__parentnode=testsubject,
                                     anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
            {testassignment1, testassignment2},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_distinct(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make('core.Period', parentnode=testsubject)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        subjectpermissiongroup1 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        subjectpermissiongroup2 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        periodpermissiongroup1 = mommy.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        periodpermissiongroup2 = mommy.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup2.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup2.permissiongroup)
        self.assertEqual(
            {testassignment},
            set(Assignment.objects.filter_user_is_admin(user=testuser)))
