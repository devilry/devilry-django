

from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone
from model_bakery import baker

from devilry.devilry_admin.views.period.overview_all_results_collector import PeriodAllResultsCollector
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_factory


class TestAllResultsCollector(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_student_for_period(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEqual(relatedstudent, collector.results[relatedstudent.id].relatedstudent)

    def test_get_result_for_assignment_feedbackset_is_published(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEqual(
            10,
            collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_result_for_assignment_feedbackset_is_unpublished(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEqual(
            0,
            collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_result_for_assignment_where_student_is_not_registered(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(
            group=testgroup,
            related_student_ids=[relatedstudent.id]
        )
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertIsNone(collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_is_waiting_for_feedback(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id))

    def test_is_not_waiting_for_feedback(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertFalse(collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id))

    def test_raises_value_error_is_waiting_for_feedback_not_registered_on_assignment(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        with self.assertRaises(ValueError):
            collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id)

    def test_is_not_waiting_for_deliveries_if_last_published_feedbackset_is_last_feedbackset(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=0,
            deadline_datetime=timezone.now() + timedelta(days=1),
        )
        group_factory.feedbackset_new_attempt_published(
            group=testgroup,
            grading_points=10,
            deadline_datetime=timezone.now() + timedelta(days=4),
        )
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertFalse(collector.results[relatedstudent.id].is_waiting_for_deliveries(testassignment.id))

    def test_is_waiting_for_deliveries(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=0,
            deadline_datetime=timezone.now() + timedelta(days=1),
        )
        group_factory.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timedelta(days=4),
        )
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(collector.results[relatedstudent.id].is_waiting_for_deliveries(testassignment.id))

    def test_is_not_waiting_for_deliveries(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10,
            deadline_datetime=timezone.now() - timedelta(days=4),
        )
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertFalse(collector.results[relatedstudent.id].is_waiting_for_deliveries(testassignment.id))

    def test_raises_value_error_is_waiting_for_deliveries_not_registered_on_assignment(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=user)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        with self.assertRaises(ValueError):
            collector.results[relatedstudent.id].is_waiting_for_deliveries(testassignment.id)

    def test_student_is_registered_on_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(
            collector.results[relatedstudent.id].student_is_registered_on_assignment(assignment_id=testassignment.id))

    def test_student_is_registered_on_two_of_three_assignments(self):
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod)
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment3)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment1.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent)
        baker.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(
            collector.results[relatedstudent.id].student_is_registered_on_assignment(assignment_id=testassignment1.id))
        self.assertFalse(
            collector.results[relatedstudent.id].student_is_registered_on_assignment(assignment_id=testassignment2.id)
        )
        self.assertTrue(
            collector.results[relatedstudent.id].student_is_registered_on_assignment(assignment_id=testassignment3.id))

    def test_students_are_registered_on_period_but_no_assignments(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # Student donald
        donald_user = baker.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)

        # Student april
        april_user = baker.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEqual(relatedstudent_donald, collector.results[relatedstudent_donald.id].relatedstudent)
        self.assertEqual(relatedstudent_april, collector.results[relatedstudent_april.id].relatedstudent)

    def test_student_points_for_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertEqual(10, relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

    def test_student_no_published_feedback_on_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertEqual(0, relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

    def test_get_result_for_assignment_only_counts_last_published_feedbackset_is_last_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        group_factory.feedbackset_new_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEqual(0, collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_total_result_only_counts_last_published_feedbackset_is_last_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudent = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        group_factory.feedbackset_new_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEqual(0, collector.results[relatedstudent.id].get_total_result())

    def test_students_in_separate_groups_points_for_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Student donald
        donald_user = baker.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        group_factory.feedbackset_first_attempt_published(group=testgroup1, grading_points=10)

        # Student april
        april_user = baker.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        baker.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_april)
        group_factory.feedbackset_first_attempt_published(group=testgroup2, grading_points=15)

        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEqual(
            10,
            collector.results[relatedstudent_donald.id].get_result_for_assignment(assignment_id=testassignment.id))
        self.assertEqual(
            15,
            collector.results[relatedstudent_april.id].get_result_for_assignment(assignment_id=testassignment.id))

    def test_students_in_same_group_points_for_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # Student donald
        donald_user = baker.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent_donald)

        # Student april
        april_user = baker.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = baker.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent_april)

        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)

        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEqual(
            10,
            collector.results[relatedstudent_donald.id].get_result_for_assignment(testassignment.id))
        self.assertEqual(
            10,
            collector.results[relatedstudent_april.id].get_result_for_assignment(testassignment.id))

    def test_student_get_total_result_for_period(self):
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod, max_points=20,
                                     passing_grade_min_points=12)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod, max_points=30,
                                     passing_grade_min_points=15)
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod, max_points=15,
                                     passing_grade_min_points=5)

        # Donald Duck on separate groups
        student_user_donald = baker.make(settings.AUTH_USER_MODEL, fullname='Donald Duck', shortname='donaldduck')
        relatedstudent_donald = baker.make('core.RelatedStudent', period=testperiod, user=student_user_donald)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment3)
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        baker.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_donald)
        baker.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent_donald)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup1,
            grading_points=10
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup2,
            grading_points=11
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup3,
            grading_points=12
        )

        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent_donald.id]
        )
        self.assertEqual(
            33,
            collector.results[relatedstudent_donald.id].get_total_result())

    def test_num_queries_sanity_test(self):
        # Tests the result collector, and a call to almost all functions.
        testperiod = baker.make('core.Period')
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod, max_points=20,
                                     passing_grade_min_points=12)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod, max_points=30,
                                     passing_grade_min_points=15)
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod, max_points=15,
                                     passing_grade_min_points=5)

        # Donald Duck on separate groups
        student_user_donald = baker.make(settings.AUTH_USER_MODEL, fullname='Donald Duck', shortname='donaldduck')
        relatedstudent_donald = baker.make('core.RelatedStudent', period=testperiod, user=student_user_donald)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment3)
        baker.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        baker.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_donald)
        baker.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent_donald)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup1,
            grading_points=10
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup2,
            grading_points=11
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup3,
            grading_points=12
        )

        # April Duck on separate groups
        student_user_april = baker.make(settings.AUTH_USER_MODEL, fullname='April Duck', shortname='aprilduck')
        relatedstudent_april = baker.make('core.RelatedStudent', period=testperiod, user=student_user_april)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup5 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup6 = baker.make('core.AssignmentGroup', parentnode=testassignment3)
        baker.make('core.Candidate', assignment_group=testgroup4, relatedstudent=relatedstudent_april)
        baker.make('core.Candidate', assignment_group=testgroup5, relatedstudent=relatedstudent_april)
        baker.make('core.Candidate', assignment_group=testgroup6, relatedstudent=relatedstudent_april)
        group_factory.feedbackset_first_attempt_published(
            group=testgroup4,
            grading_points=20
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup5,
            grading_points=30
        )
        group_factory.feedbackset_first_attempt_published(
            group=testgroup6,
            grading_points=15
        )
        with self.assertNumQueries(2):
            collector = PeriodAllResultsCollector(
                period=testperiod,
                related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
            )
            collector.results[relatedstudent_donald.id].student_is_registered_on_assignment(testassignment1.id)
            collector.results[relatedstudent_donald.id].student_is_registered_on_assignment(testassignment2.id)
            collector.results[relatedstudent_donald.id].student_is_registered_on_assignment(testassignment3.id)

            collector.results[relatedstudent_april.id].student_is_registered_on_assignment(testassignment1.id)
            collector.results[relatedstudent_april.id].student_is_registered_on_assignment(testassignment2.id)
            collector.results[relatedstudent_april.id].student_is_registered_on_assignment(testassignment3.id)

            collector.results[relatedstudent_donald.id].is_waiting_for_feedback(testassignment1.id)
            collector.results[relatedstudent_donald.id].is_waiting_for_feedback(testassignment2.id)
            collector.results[relatedstudent_donald.id].is_waiting_for_feedback(testassignment3.id)

            collector.results[relatedstudent_april.id].is_waiting_for_feedback(testassignment1.id)
            collector.results[relatedstudent_april.id].is_waiting_for_feedback(testassignment2.id)
            collector.results[relatedstudent_april.id].is_waiting_for_feedback(testassignment3.id)

            collector.results[relatedstudent_donald.id].get_result_for_assignment(testassignment1.id)
            collector.results[relatedstudent_donald.id].get_result_for_assignment(testassignment2.id)
            collector.results[relatedstudent_donald.id].get_result_for_assignment(testassignment3.id)

            collector.results[relatedstudent_april.id].get_result_for_assignment(testassignment1.id)
            collector.results[relatedstudent_april.id].get_result_for_assignment(testassignment2.id)
            collector.results[relatedstudent_april.id].get_result_for_assignment(testassignment3.id)

            collector.results[relatedstudent_donald.id].get_total_result()

            collector.results[relatedstudent_april.id].get_total_result()

            collector.results[relatedstudent_donald.id].get_cached_data_list()

            collector.results[relatedstudent_april.id].get_cached_data_list()

            collector.serialize_all_results()
