from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

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
from devilry.apps.core.models import Period, Examiner
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
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   student__shortname='student1')
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   student__shortname='student2')

        targetassignment = mommy.make('core.Assignment')
        targetassignment.copy_groups_from_another_assignment(sourceassignment)
        self.assertEqual(targetassignment.assignmentgroups.count(), 2)
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=targetassignment)
        self.assertTrue(candidatesqueryset.filter(student__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(student__shortname='student2').exists())

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

    def test_copy_groups_from_another_assignment_candidateids_handling_per_period(self):
        sourceassignment = mommy.make('core.Assignment')
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   candidate_id='a',
                   automatic_anonymous_id='autoa',
                   )
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   candidate_id='b',
                   automatic_anonymous_id='autob')

        targetassignment = mommy.make('core.Assignment')
        with self.settings(DEVILRY_CANDIDATE_ID_HANDLING='per-period'):
            targetassignment.copy_groups_from_another_assignment(sourceassignment)
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=targetassignment)
        self.assertTrue(candidatesqueryset.filter(candidate_id='a').exists())
        self.assertTrue(candidatesqueryset.filter(candidate_id='b').exists())
        self.assertTrue(candidatesqueryset.filter(automatic_anonymous_id='autoa').exists())
        self.assertTrue(candidatesqueryset.filter(automatic_anonymous_id='autob').exists())

    def test_copy_groups_from_another_assignment_candidateids_handling_none(self):
        sourceassignment = mommy.make('core.Assignment')
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   candidate_id='a')
        mommy.make('core.Candidate',
                   assignment_group__parentnode=sourceassignment,
                   candidate_id='b')

        targetassignment = mommy.make('core.Assignment')
        with self.settings(DEVILRY_CANDIDATE_ID_HANDLING=None):
            targetassignment.copy_groups_from_another_assignment(sourceassignment)
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=targetassignment)
        self.assertFalse(candidatesqueryset.filter(candidate_id='a').exists())
        self.assertFalse(candidatesqueryset.filter(candidate_id='b').exists())

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

        qry = Assignment.objects.filter_is_examiner(examiner1)
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
