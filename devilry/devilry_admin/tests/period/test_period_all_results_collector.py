from __future__ import unicode_literals

from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.devilry_admin.views.period.overview_all_results_collector import PeriodAllResultsCollector
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_factory


class TestAllResultsCollector(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_student_for_period(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEquals(relatedstudent, collector.results[relatedstudent.id].relatedstudent)

    def test_get_result_for_assignment_feedbackset_is_published(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEquals(
            10,
            collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_result_for_assignment_feedbackset_is_unpublished(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEquals(
            0,
            collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_result_for_assignment_where_student_is_not_registered(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', relatedstudent=relatedstudent)
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
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id))

    def test_is_not_waiting_for_feedback(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        self.assertFalse(collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id))

    def test_raises_value_error_is_waiting_for_feedback_not_registered_on_assignment(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, user=user)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testperiod,
            related_student_ids=[relatedstudent.id]
        )
        with self.assertRaises(ValueError):
            collector.results[relatedstudent.id].is_waiting_for_feedback(testassignment.id)

    def test_student_is_registered_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertTrue(
            collector.results[relatedstudent.id].student_is_registered_on_assignment(assignment_id=testassignment.id))

    def test_student_is_registered_on_two_of_three_assignments(self):
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment3 = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment3)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment1.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent)
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
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # Student donald
        donald_user = mommy.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)

        # Student april
        april_user = mommy.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEquals(relatedstudent_donald, collector.results[relatedstudent_donald.id].relatedstudent)
        self.assertEquals(relatedstudent_april, collector.results[relatedstudent_april.id].relatedstudent)

    def test_student_points_for_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertEquals(10, relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

    def test_student_no_published_feedback_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertEquals(0, relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

    def test_get_result_for_assignment_only_counts_last_published_feedbackset_is_last_feedbackset(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        group_factory.feedbackset_new_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEquals(0, collector.results[relatedstudent.id].get_result_for_assignment(testassignment.id))

    def test_get_total_result_only_counts_last_published_feedbackset_is_last_feedbackset(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        group_factory.feedbackset_new_attempt_unpublished(group=testgroup)
        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent.id]
        )
        self.assertEquals(0, collector.results[relatedstudent.id].get_total_result())

    def test_students_in_separate_groups_points_for_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # Student donald
        donald_user = mommy.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        group_factory.feedbackset_first_attempt_published(group=testgroup1, grading_points=10)

        # Student april
        april_user = mommy.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_april)
        group_factory.feedbackset_first_attempt_published(group=testgroup2, grading_points=15)

        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEquals(
            10,
            collector.results[relatedstudent_donald.id].get_result_for_assignment(assignment_id=testassignment.id))
        self.assertEquals(
            15,
            collector.results[relatedstudent_april.id].get_result_for_assignment(assignment_id=testassignment.id))

    def test_students_in_same_group_points_for_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # Student donald
        donald_user = mommy.make(settings.AUTH_USER_MODEL, fullname='Donald', shortname='donald')
        relatedstudent_donald = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=donald_user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent_donald)

        # Student april
        april_user = mommy.make(settings.AUTH_USER_MODEL, fullname='April', shortname='april')
        relatedstudent_april = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=april_user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent_april)

        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=10)

        # Run collector
        collector = PeriodAllResultsCollector(
            period=testassignment.parentnode,
            related_student_ids=[relatedstudent_donald.id, relatedstudent_april.id]
        )
        self.assertEquals(
            10,
            collector.results[relatedstudent_donald.id].get_result_for_assignment(testassignment.id))
        self.assertEquals(
            10,
            collector.results[relatedstudent_april.id].get_result_for_assignment(testassignment.id))

    def test_student_get_total_result_for_period(self):
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod, max_points=20,
                                     passing_grade_min_points=12)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod, max_points=30,
                                     passing_grade_min_points=15)
        testassignment3 = mommy.make('core.Assignment', parentnode=testperiod, max_points=15,
                                     passing_grade_min_points=5)

        # Donald Duck on separate groups
        student_user_donald = mommy.make(settings.AUTH_USER_MODEL, fullname='Donald Duck', shortname='donaldduck')
        relatedstudent_donald = mommy.make('core.RelatedStudent', period=testperiod, user=student_user_donald)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment3)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_donald)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent_donald)
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
        self.assertEquals(
            33,
            collector.results[relatedstudent_donald.id].get_total_result())

    def test_num_queries_sanity_test(self):
        # Tests the result collector, and a call to almost all functions.
        testperiod = mommy.make('core.Period')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod, max_points=20,
                                     passing_grade_min_points=12)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod, max_points=30,
                                     passing_grade_min_points=15)
        testassignment3 = mommy.make('core.Assignment', parentnode=testperiod, max_points=15,
                                     passing_grade_min_points=5)

        # Donald Duck on separate groups
        student_user_donald = mommy.make(settings.AUTH_USER_MODEL, fullname='Donald Duck', shortname='donaldduck')
        relatedstudent_donald = mommy.make('core.RelatedStudent', period=testperiod, user=student_user_donald)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment3)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent=relatedstudent_donald)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent=relatedstudent_donald)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent=relatedstudent_donald)
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
        student_user_april = mommy.make(settings.AUTH_USER_MODEL, fullname='April Duck', shortname='aprilduck')
        relatedstudent_april = mommy.make('core.RelatedStudent', period=testperiod, user=student_user_april)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        testgroup6 = mommy.make('core.AssignmentGroup', parentnode=testassignment3)
        mommy.make('core.Candidate', assignment_group=testgroup4, relatedstudent=relatedstudent_april)
        mommy.make('core.Candidate', assignment_group=testgroup5, relatedstudent=relatedstudent_april)
        mommy.make('core.Candidate', assignment_group=testgroup6, relatedstudent=relatedstudent_april)
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
