from __future__ import unicode_literals

from django import test
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_admin.views.period import overview_all_results_collector
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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
        self.assertEquals(relatedstudent, collector.results[relatedstudent.id].relatedstudent)

    def test_student_is_registered_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testperiod)
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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertEquals(10, relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

    def test_student_no_published_feedback_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user=user)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        # Run collector
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
        relatedstudent_results = collector.results[relatedstudent.id]
        self.assertIsNone(relatedstudent_results.get_result_for_assignment(assignment_id=testassignment.id))

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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
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
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testassignment.parentnode)
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

        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testperiod)
        self.assertEquals(
            33,
            collector.results[relatedstudent_donald.id].get_total_result())

    def test_serialized_data(self):
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

        comparison_dict = {
            'relatedstudents':
                [
                    {
                        'relatedstudent_id': relatedstudent_donald.id,
                        'user':
                            {
                                'id': student_user_donald.id,
                                'shortname': student_user_donald.shortname,
                                'fullname': student_user_donald.fullname
                            },
                        'assignments':
                            [
                                {
                                    'id': testassignment1.id,
                                    'result': 10
                                },
                                {
                                    'id': testassignment2.id,
                                    'result': 11
                                },
                                {
                                    'id': testassignment3.id,
                                    'result': 12
                                }
                            ]
                    },
                ],
        }
        collector = overview_all_results_collector.PeriodAllResultsCollector(period=testperiod)
        serialized_results = collector.serialize_all_results()
        self.assertEquals(0, cmp(comparison_dict, serialized_results))

    def test_serialized_data_two_students(self):
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

        comparison_dict = {
            'relatedstudents':
                [
                    {
                        'relatedstudent_id': relatedstudent_donald.id,
                        'user':
                            {
                                'id': student_user_donald.id,
                                'shortname': student_user_donald.shortname,
                                'fullname': student_user_donald.fullname
                            },
                        'assignments':
                            [
                                {
                                    'id': testassignment1.id,
                                    'result': 10
                                },
                                {
                                    'id': testassignment2.id,
                                    'result': 11
                                },
                                {
                                    'id': testassignment3.id,
                                    'result': 12
                                }
                            ]
                    },
                    {
                        'relatedstudent_id': relatedstudent_april.id,
                        'user':
                            {
                                'id': student_user_april.id,
                                'shortname': student_user_april.shortname,
                                'fullname': student_user_april.fullname
                            },
                        'assignments':
                            [
                                {
                                    'id': testassignment1.id,
                                    'result': 20
                                },
                                {
                                    'id': testassignment2.id,
                                    'result': 30
                                },
                                {
                                    'id': testassignment3.id,
                                    'result': 15
                                }
                            ]
                    },
                ],
        }
        with self.assertNumQueries(2):
            collector = overview_all_results_collector.PeriodAllResultsCollector(period=testperiod)
            serialized_results = collector.serialize_all_results()
            self.assertEquals(0, cmp(comparison_dict, serialized_results))

    def test_num_queries(self):
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
            overview_all_results_collector\
                .PeriodAllResultsCollector(period=testperiod)
