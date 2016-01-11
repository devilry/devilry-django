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
        self.assertEquals(assignment1.points_to_grade(0), 'Failed')
        self.assertEquals(assignment1.points_to_grade(1), 'Passed')

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
                   relatedstudent__user=student1,
                   student=student1)
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   relatedstudent__user=student2,
                   student=student2)

        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 2)
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=targetassignment)
        self.assertTrue(candidatesqueryset.filter(student__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(student__shortname='student2').exists())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student2').exists())

    def test_copy_groups_from_another_assignment_examiners(self):
        sourceassignment = mommy.make('core.Assignment')
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=sourceassignment,
                   user__shortname='examiner1')
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=sourceassignment,
                   user__shortname='examiner2')

        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 2)
        candidatesqueryset = Examiner.objects.filter(assignmentgroup__parentnode=targetassignment)
        self.assertTrue(candidatesqueryset.filter(user__shortname='examiner1').exists())
        self.assertTrue(candidatesqueryset.filter(user__shortname='examiner2').exists())

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
        self.assertTrue(candidatesqueryset.filter(student__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(student__shortname='student2').exists())
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
        self.assertTrue(group1.examiners.filter(user__shortname='examiner1').exists())

    def test_setup_examiners_by_relateduser_syncsystem_tags_exclude_existing_examinerobjects(self):
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
        mommy.make('core.Examiner', assignmentgroup=group1,
                   user=examiner1)

        # NOTE: The real test here is that we do not get an IntegrityError
        self.assertEqual(group1.examiners.count(), 1)
        testassignment.setup_examiners_by_relateduser_syncsystem_tags()
        group1 = AssignmentGroup.objects.get(id=group1.id)
        self.assertEqual(group1.examiners.count(), 1)
        self.assertTrue(group1.examiners.filter(user__shortname='examiner1').exists())

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
        self.assertTrue(group1.examiners.filter(user__shortname='examiner1').exists())
        self.assertFalse(group1.examiners.filter(user__shortname='examiner2').exists())
        self.assertEqual(group2.examiners.count(), 2)
        self.assertTrue(group2.examiners.filter(user__shortname='examiner1').exists())
        self.assertTrue(group2.examiners.filter(user__shortname='examiner2').exists())

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


class TestAssignmentOld(TestCase, TestHelper):
    """
    Do not add new tests to this testcase, use TestAssignment and
    corebuilder instead.
    """

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong:begins(-1):ends(10)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)", "g2:examiner(examiner2)",
                                   "g3:candidate(student2,student3):examiner(examiner1,examiner2)"])
        self.add_to_path('uio.ifi;inf1100.looong.assignment3.group1:examiner(examiner1)')
        self.add_to_path('uio.ifi;inf1100.old.oldassignment.group1:examiner(examiner3)')

    def test_is_active(self):
        self.assertTrue(self.inf1100_looong_assignment1.is_active())
        self.assertFalse(self.inf1100_old_assignment1.is_active())

        # Move assignments pubtime to future, and check that it is no longer active
        self.inf1100_looong_assignment1.publishing_time = datetime.now() + timedelta(days=1)
        self.inf1100_looong_assignment1.save()
        self.assertFalse(self.inf1100_looong_assignment1.is_active())

    def test_first_deadline_clean_ok(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.first_deadline = assignment1.parentnode.start_time + timedelta(days=1)
        assignment1.clean()

    def test_first_deadline_clean_perioderror(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.first_deadline = assignment1.parentnode.start_time - timedelta(days=10)
        errors = {}
        assignment1._clean_first_deadline(errors)
        self.assertIn('first_deadline', errors)

        with self.assertRaises(ValidationError):
            assignment1.clean()

        assignment1.first_deadline = assignment1.parentnode.end_time + timedelta(days=10)
        errors = {}
        assignment1._clean_first_deadline(errors)
        self.assertIn('first_deadline', errors)
        with self.assertRaises(ValidationError):
            assignment1.clean()

        assignment1.first_deadline = assignment1.parentnode.start_time + timedelta(days=1)
        assignment1.clean()

    def test_unique(self):
        n = Assignment(parentnode=Period.objects.get(
            short_name='looong'),
            short_name='assignment1', long_name='O1',
            publishing_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def anon_change_anonymous(self):
        self.inf1100_looong_assignment1.anonymous = True
        self.inf1100_looong_assignment1.save()
        candidates = Candidate.objects.filter(
            Q(assignment_group__parentnode__id=self.inf1100_looong_assignment1.id))
        for can in candidates:
            self.assertEquals(can.candidate_id, can.identifier)
        self.inf1100_looong_assignment1.anonymous = False
        self.inf1100_looong_assignment1.save()
        candidates = Candidate.objects.filter(
            Q(assignment_group__parentnode__id=self.inf1100_looong_assignment1.id))
        for can in candidates:
            self.assertEquals(can.student.username, can.identifier)

    def test_where_is_admin(self):
        ifiadmin = get_user_model().objects.get(shortname='ifiadmin')
        self.assertEquals(Assignment.where_is_admin(ifiadmin).count(), 6)

    def test_where_is_examiner(self):
        examiner3 = get_user_model().objects.get(shortname='examiner3')
        q = Assignment.where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')
        self.inf1100_looong_assignment3_group1.examiners.create(user=examiner3)
        self.assertEquals(q.count(), 2)

    def test_published_where_is_examiner(self):
        get_user_model().objects.get(shortname='examiner3')
        q = Assignment.published_where_is_examiner(self.examiner3, old=False, active=False)
        self.assertEquals(q.count(), 0)

        q = Assignment.published_where_is_examiner(self.examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')

        # Add as examiner, count should increase
        self.inf1100_looong_assignment1_g1.examiners.create(user=self.examiner3)
        self.assertEquals(q.count(), 2)
        # Set publishing_time to future. count should decrease
        self.inf1100_looong_assignment1.publishing_time = datetime.now() + timedelta(10)
        self.inf1100_looong_assignment1.save()
        q = Assignment.published_where_is_examiner(self.examiner3)
        self.assertEquals(q.count(), 1)

    def test_active_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner1 = get_user_model().objects.get(shortname='examiner1')
        # Get assignments where the period is active
        q = Assignment.active_where_is_examiner(examiner1).order_by('short_name')
        self.assertEquals(q.count(), 3)
        self.assertEquals(q[0].short_name, 'assignment1')
        self.assertEquals(q[1].short_name, 'assignment2')
        self.assertEquals(q[2].short_name, 'assignment3')

        # Create group2 with examiner1 as examiner
        self.add_to_path('uio.ifi;inf1010.spring10:begins(-1):ends(2).assignment0.group2:examiner(examiner1)')
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 4)
        self.inf1010_spring10.end_time = past
        self.inf1010_spring10.save()
        self.assertEquals(q.count(), 3)
        self.inf1010_spring10_assignment0.publishing_time = past
        self.inf1010_spring10_assignment0.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 3)

    def test_old_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner3 = get_user_model().objects.get(shortname='examiner3')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldassignment')

        # Set as examiner on group1
        self.add_to_path('uio.ifi;inf1100.looong.assignment1.group1:examiner(examiner3)')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        # Making the period old and verify that the count has changed
        self.inf1100_looong.end_time = past
        self.inf1100_looong.save()
        self.assertEquals(q.count(), 2)

    def test_clean_publishing_time_before(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.parentnode.start_time = datetime(2010, 1, 1)
        assignment1.parentnode.end_time = datetime(2011, 1, 1)
        assignment1.publishing_time = datetime(2010, 1, 2)
        assignment1.clean()
        assignment1.publishing_time = datetime(2009, 1, 1)
        self.assertRaises(ValidationError, assignment1.clean)

    def test_clean_publishing_time_after(self):
        assignment1 = self.inf1100_looong_assignment1
        assignment1.parentnode.start_time = datetime(2010, 1, 1)
        assignment1.parentnode.end_time = datetime(2011, 1, 1)
        assignment1.publishing_time = datetime(2010, 1, 2)
        assignment1.clean()
        assignment1.publishing_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, assignment1.clean)

    def test_get_path(self):
        self.assertEquals(self.inf1100_looong_assignment1.get_path(), 'inf1100.looong.assignment1')

    def test_is_empty(self):
        self.add(nodes="uio.ifi",
                 subjects=['duck9000'],
                 periods=['someperiod:begins(-2)'],
                 assignments=['a1'])
        self.assertTrue(self.duck9000_someperiod_a1.is_empty())
        self.add_to_path('uni.ifi;duck9000.someperiod.a1.g1:candidate(stud1).d1:ends(5)')
        self.add_delivery("duck9000.someperiod.a1.g1", {"good.py": "print awesome"})
        self.assertFalse(self.duck9000_someperiod_a1.is_empty())


class TestAssignmentCanDelete(TestCase, TestHelper):
    def setUp(self):
        self.goodFile = {"good.py": "print awesome"}

    def test_can_delete_superuser(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1.g1:candidate(stud1).d1:ends(5)')
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        superuser = self.create_superuser('superuser')
        assignment = Assignment.objects.get(id=self.sub_p1_a1.id)
        self.assertTrue(assignment.can_delete(superuser))

    def test_can_delete_assignmentadmin(self):
        self.add_to_path('uni;sub.p1:begins(-2).a1:admin(a1admin)')
        assignment = Assignment.objects.get(id=self.sub_p1_a1.id)
        self.assertFalse(assignment.can_delete(self.a1admin))

    def test_can_delete_periodadmin(self):
        self.add_to_path('uni;sub.p1:begins(-2):admin(p1admin).a1.g1:candidate(stud1).d1:ends(5)')
        assignment = Assignment.objects.get(id=self.sub_p1_a1.id)
        self.assertTrue(assignment.can_delete(self.p1admin))
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        self.assertFalse(assignment.can_delete(self.p1admin))

    def test_can_delete_nodeadmin(self):
        self.add_to_path('uni:admin(uniadm);sub.p1:begins(-2).a1.g1:candidate(stud1).d1:ends(5)')
        assignment = Assignment.objects.get(id=self.sub_p1_a1.id)
        self.assertTrue(assignment.can_delete(self.uniadm))
        self.add_delivery("sub.p1.a1.g1", self.goodFile)
        self.assertFalse(assignment.can_delete(self.uniadm))


class TestAssignmentQuerySet(TestCase):
    def test_annotate_with_waiting_for_feedback_count_nomatch_deadline_not_expired(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() + timedelta(days=1),
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_deadline_not_expired_first_feedbackset(self):
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode__first_deadline=timezone.now() + timedelta(days=1),
                   grading_published_datetime=None,
                   deadline_datetime=None,
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_is_not_last_in_group(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=None)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_nomatch_grading_published(self):
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(0, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_in_same_group(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(1, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_groups(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=timezone.now() - timedelta(days=1),
                   deadline_datetime=timezone.now() - timedelta(days=2),
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=None,
                   deadline_datetime=timezone.now() - timedelta(days=1),
                   is_last_in_group=True)
        queryset = Assignment.objects.all().annotate_with_waiting_for_feedback_count()
        self.assertEqual(2, queryset.first().waiting_for_feedback_count)

    def test_annotate_with_waiting_for_feedback_count_match_multiple_assignments(self):
        testassignment1 = mommy.make('core.Assignment')
        testassignment2 = mommy.make('core.Assignment')
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


class TestAssignmentManager(TestCase):

    def test_filter_admin_has_access_directly_on_assignment(self):
        admin1 = UserBuilder('admin1').user
        periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        assignment1 = periodbuilder.add_assignment('assignment1').add_admins(admin1).assignment
        periodbuilder.add_assignment('assignment2')
        qry = Assignment.objects.filter_admin_has_access(admin1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], assignment1)

    def test_filter_admin_has_access_recursive_from_subject(self):
        admin1 = UserBuilder('admin1').user
        nodebuilder = NodeBuilder('docku')
        assignment1 = nodebuilder.add_subject('subject1')\
            .add_admins(admin1)\
            .add_6month_active_period()\
            .add_assignment('assignment1').assignment
        nodebuilder.add_subject('subject2')\
            .add_6month_active_period()\
            .add_assignment('assignment2')
        qry = Assignment.objects.filter_admin_has_access(admin1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], assignment1)

    def test_filter_admin_has_access_recursive_from_node(self):
        admin1 = UserBuilder('admin1').user
        nodebuilder = NodeBuilder('docku')
        assignment1 = nodebuilder\
            .add_childnode('science').add_admins(admin1)\
            .add_childnode('inf')\
            .add_subject('subject1')\
            .add_6month_active_period()\
            .add_assignment('assignment1').assignment
        nodebuilder\
            .add_subject('subject2')\
            .add_6month_active_period()\
            .add_assignment('assignment2')
        qry = Assignment.objects.filter_admin_has_access(admin1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], assignment1)

    def test_filter_is_examiner(self):
        examiner1 = UserBuilder('examiner1').user
        week1builder = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        week1builder.add_group().add_examiners(examiner1)

        # Add another group to make sure we do not get false positives
        week1builder.add_group().add_examiners(UserBuilder('examiner2').user)

        qry = Assignment.objects.filter_user_is_examiner(examiner1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], week1builder.assignment)

    def test_filter_is_active(self):
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        activeassignmentbuilder = duck1010builder.add_6month_active_period().add_assignment('week1')

        # Add inactive groups to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1')
        duck1010builder.add_6month_nextyear_period().add_assignment('week1')

        qry = Assignment.objects.filter_is_active()
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], activeassignmentbuilder.assignment)

    def test_filter_examiner_has_access(self):
        examiner1 = UserBuilder('examiner1').user
        otherexaminer = UserBuilder('otherexaminer').user
        duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        activeassignmentbuilder = duck1010builder.add_6month_active_period().add_assignment('week1')
        activeassignmentbuilder.add_group().add_examiners(examiner1)

        # Add inactive groups and a group with another examiner to make sure we get no false positives
        duck1010builder.add_6month_lastyear_period().add_assignment('week1')\
            .add_group().add_examiners(examiner1)
        duck1010builder.add_6month_nextyear_period().add_assignment('week1')\
            .add_group().add_examiners(examiner1)
        activeassignmentbuilder.add_group().add_examiners(otherexaminer)

        qry = Assignment.objects.filter_examiner_has_access(examiner1)
        self.assertEquals(qry.count(), 1)
        self.assertEquals(qry[0], activeassignmentbuilder.assignment)

        # make sure we are not getting false positives
        self.assertEquals(Assignment.objects.filter_is_examiner(examiner1).count(), 3)
        self.assertEquals(Assignment.objects.filter_is_examiner(otherexaminer).count(), 1)

    def test_filter_user_is_examiner(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make('core.Assignment')
        assignmentgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedexaminer = mommy.make('core.RelatedExaminer', user=user, assignmentgroup=assignmentgroup)
        examiner = mommy.make('core.Examiner', relatedexaminer=relatedexaminer)
        mommy.make('core.AssignmentGroup', examiners=[examiner])
        queryset = Assignment.objects.filter_user_is_examiner(user)
        self.assertEquals(queryset.count(), 1)
        returned_assignment = queryset.first()
        self.assertTrue(assignment.id, returned_assignment.id)

    def test_filter_user_is_not_examiner(self):
        user_not_set_as_examiner = mommy.make(settings.AUTH_USER_MODEL)
        relatedexaminer = mommy.make('core.RelatedExaminer')
        examiner = mommy.make('core.Examiner', relatedexaminer=relatedexaminer)
        mommy.make('core.AssignmentGroup', examiners=[examiner])
        queryset = Assignment.objects.filter_user_is_examiner(user_not_set_as_examiner)
        self.assertEquals(queryset.count(), 0)

