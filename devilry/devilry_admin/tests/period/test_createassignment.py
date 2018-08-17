import unittest
from datetime import timedelta

import htmls
import mock
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from django_cradmin import crinstance
from model_mommy import mommy

from devilry.apps.core.models import Assignment, Candidate, Examiner, AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_END, ACTIVE_PERIOD_START, OLD_PERIOD_START, FUTURE_PERIOD_END, \
    ASSIGNMENT_FUTUREPERIOD_START_FIRST_DEADLINE
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_admin.views.period import createassignment
from devilry.utils import datetimeutils
from devilry.utils.datetimeutils import default_timezone_datetime


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createassignment.CreateView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_render_formfields(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=first_deadline]'))

    def test_get_suggested_name_first_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_not_suffixed_with_number(self):
        period = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                   long_name='Test', short_name='test').period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_suffixed_with_number(self):
        period = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                   long_name='Test1', short_name='test1').period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), 'Test2')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), 'test2')

    @unittest.skip('Must be revised. Depends on Assignment.first_deadline being None.')
    def test_get_suggested_name_previous_assignment_suffixed_with_number_namecollision_no_first_deadline(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          long_name='Test1', short_name='test1')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          long_name='Test2', short_name='test2',
                          first_deadline=None)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_suffixed_with_number_namecollision_strange_order(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          long_name='Test1', short_name='test1',
                          first_deadline=ACTIVE_PERIOD_END)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          long_name='Test2', short_name='test2',
                          first_deadline=ACTIVE_PERIOD_START)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_deadlines_first_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertFalse(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    def test_get_suggested_deadlines_not_first_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start').period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertTrue(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    @unittest.skip('Must be revised. Depends on Assignment.first_deadline being None.')
    def test_get_suggested_deadlines_not_first_assignment_no_previous_with_deadline(self):
        period = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=None).period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        self.assertFalse(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    def test_get_suggested_deadlines_render_values_previous_deadline_in_the_past(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')

        # Ignored by the suggestion system
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period)

        # This should be the one that is used for suggestions
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          first_deadline=default_timezone_datetime(2015, 9, 2, 13, 30))  # Wed

        timezonemock = mock.MagicMock()
        timezonemock.now.return_value = default_timezone_datetime(2015, 9, 10, 22, 18)  # Thursday
        with mock.patch('devilry.devilry_admin.views.period.createassignment.timezone', timezonemock):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=period)
        suggested_deadline_elements = mockresponse.selector.list(
            '.devilry-admin-createassignment-suggested-deadline')
        suggested_deadline_values = [element['django-cradmin-setfieldvalue']
                                     for element in suggested_deadline_elements]
        self.assertEqual(suggested_deadline_values, [
            '2015-09-16 13:30',
            '2015-09-23 13:30',
            '2015-09-30 13:30',
            '2015-10-07 13:30',
        ])

    def test_get_suggested_deadlines_render_values_previous_deadline_in_the_future(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')

        # Ignored by the suggestion system
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period)

        # This should be the one that is used for suggestions
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          first_deadline=default_timezone_datetime(3500, 9, 5, 13, 30))

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        suggested_deadline_elements = mockresponse.selector.list(
            '.devilry-admin-createassignment-suggested-deadline')
        suggested_deadline_values = [element['django-cradmin-setfieldvalue']
                                     for element in suggested_deadline_elements]
        self.assertEqual(suggested_deadline_values, [
            '3500-09-12 13:30',
            '3500-09-19 13:30',
            '3500-09-26 13:30',
            '3500-10-03 13:30',
        ])

    def test_get_suggested_deadlines_render_labels(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')

        # Ignored by the suggestion system
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period)

        # This should be the one that is used for suggestions
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=period,
                          first_deadline=default_timezone_datetime(3500, 9, 5, 13, 30))

        with self.settings(DATETIME_FORMAT='D M j Y H:i', USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=period)
        suggested_deadline_elements = mockresponse.selector.list(
            '.devilry-admin-createassignment-suggested-deadline')
        suggested_deadline_labels = [element.alltext_normalized
                                     for element in suggested_deadline_elements]
        self.assertEqual([
            'Wed Sep 12 3500 13:30',
            'Wed Sep 19 3500 13:30',
            'Wed Sep 26 3500 13:30',
            'Wed Oct 3 3500 13:30',
        ], suggested_deadline_labels)

    def test_get_default_select_options_count(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        option_list = mockresponse.selector.list('option')
        self.assertEqual(len(option_list), 3)

    def test_get_select_options_default_selected_no_value(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        option_list = mockresponse.selector.list('option')
        self.assertEqual(option_list[0].get('value'), '')
        self.assertIsNotNone(option_list[0].get('selected', None))

    def test_get_select_options_import_all_students_on_semester_exists(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        option_list = mockresponse.selector.list('option')
        self.assertEqual(option_list[1].get('value'), 'all')

    def test_get_select_options_import_no_students_exists(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        option_list = mockresponse.selector.list('option')
        self.assertEqual(option_list[2].get('value'), 'none')

    def test_get_select_options_period_has_one_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode=period,
                                       long_name='Test1', short_name='test1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        selector = htmls.S(mockresponse.selector.one('optgroup').prettify())
        self.assertEqual(selector.one('optgroup').get('label'), assignment.long_name)
        optgroup_options = selector.list('option')
        self.assertEqual(optgroup_options[0].get('value'), '{}_all'.format(assignment.id))
        self.assertEqual(optgroup_options[1].get('value'), '{}_passed'.format(assignment.id))

    def test_get_select_options_period_has_multiple_assignments_ordered_by_first_deadline(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        first_deadline=timezone.now() + timezone.timedelta(days=1),
                                        parentnode=period, long_name='Test1', short_name='test1')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        first_deadline=timezone.now() + timezone.timedelta(days=4),
                                        parentnode=period, long_name='Test2', short_name='test2')
        assignment3 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        first_deadline=timezone.now() + timezone.timedelta(days=2),
                                        parentnode=period, long_name='Test3', short_name='test3')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        optgroup_list = mockresponse.selector.list('optgroup')
        self.assertEqual(len(optgroup_list), 3)
        self.assertEqual(optgroup_list[0].get('label'), assignment2.long_name)
        self.assertEqual(optgroup_list[1].get('label'), assignment3.long_name)
        self.assertEqual(optgroup_list[2].get('label'), assignment1.long_name)

    def test_get_select_options_period_has_multiple_assignments_options(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        first_deadline=timezone.now() + timezone.timedelta(days=1),
                                        parentnode=period, long_name='Test1', short_name='test1')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        first_deadline=timezone.now() + timezone.timedelta(days=2),
                                        parentnode=period, long_name='Test2', short_name='test2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period)
        optgroup_list = mockresponse.selector.list('optgroup')

        # Test assigment2 options
        assignment2_optgroup_selector = htmls.S(optgroup_list[0].prettify())
        assignment2_optgroup_options = assignment2_optgroup_selector.list('option')
        self.assertEqual(len(assignment2_optgroup_options), 2)
        self.assertEqual(assignment2_optgroup_options[0].get('value'), '{}_all'.format(assignment2.id))
        self.assertEqual(assignment2_optgroup_options[1].get('value'), '{}_passed'.format(assignment2.id))

        # Test assignment1 options
        assignment1_optgroup_selector = htmls.S(optgroup_list[1].prettify())
        assignment1_optgroup_options = assignment1_optgroup_selector.list('option')
        self.assertEqual(len(assignment1_optgroup_options), 2)
        self.assertEqual(assignment1_optgroup_options[0].get('value'), '{}_all'.format(assignment1.id))
        self.assertEqual(assignment1_optgroup_options[1].get('value'), '{}_passed'.format(assignment1.id))

    def test_post_missing_short_name(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        first_deadline_isoformat = datetimeutils.isoformat_noseconds(OLD_PERIOD_START)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': '',
                    'first_deadline': first_deadline_isoformat,
                }
            })
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def test_post_missing_long_name(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        first_deadline_isoformat = datetimeutils.isoformat_noseconds(OLD_PERIOD_START)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': '',
                    'short_name': 'testassignment',
                    'first_deadline': first_deadline_isoformat,
                }
            })
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_long_name').alltext_normalized)

    def test_post_missing_first_deadline(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': '',
                }
            })
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized)

    def test_post_missing_student_import_option(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(OLD_PERIOD_START),
                    'student_import_option': ''
                }
            })
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_student_import_option').alltext_normalized)

    def test_post_import_all_students_on_semester(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        relatedstudent1 = mommy.make('core.RelatedStudent', period=period)
        relatedstudent2 = mommy.make('core.RelatedStudent', period=period)
        relatedstudent3 = mommy.make('core.RelatedStudent', period=period)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': 'all'
                }
            })
        self.assertEqual(Assignment.objects.count(), 1)
        created_assignment = Assignment.objects.get()
        self.assertEqual(
            Candidate.objects
                .filter(assignment_group__parentnode=created_assignment, relatedstudent=relatedstudent1)
                .count(), 1)
        self.assertEqual(
            Candidate.objects
                .filter(assignment_group__parentnode=created_assignment, relatedstudent=relatedstudent2)
                .count(), 1)
        self.assertEqual(
            Candidate.objects
                .filter(assignment_group__parentnode=created_assignment, relatedstudent=relatedstudent3)
                .count(), 1)

    def test_post_import_all_students_on_semester_no_students_on_semester(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': 'all'
                }
            })
        self.assertEqual(Assignment.objects.count(), 1)
        created_assignment = Assignment.objects.get()
        self.assertFalse(AssignmentGroup.objects.filter(parentnode=created_assignment).exists())
        self.assertFalse(Candidate.objects.filter(assignment_group__parentnode=created_assignment).exists())

    def test_post_import_no_students(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.RelatedStudent', period=period, _quantity=10)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': 'none'
                }
            })
        self.assertEqual(Assignment.objects.count(), 1)
        created_assignment = Assignment.objects.get()
        self.assertFalse(Candidate.objects.filter(assignment_group__parentnode=created_assignment).exists())
        self.assertFalse(AssignmentGroup.objects.filter(parentnode=created_assignment).exists())

    def test_post_copy_all_students_from_another_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        relatedstudent_user1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent_user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', assignment_group__parentnode=other_assignment,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user1)
        mommy.make('core.Candidate', assignment_group__parentnode=other_assignment,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user2)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': '{}_all'.format(other_assignment.id)
                }
            })
        self.assertEqual(Assignment.objects.filter(short_name='testassignment').count(), 1)
        created_assignment = Assignment.objects.get(short_name='testassignment')
        self.assertEqual(created_assignment.assignmentgroups.count(), 2)
        self.assertEqual(
            Candidate.objects.filter(
                assignment_group__parentnode=created_assignment, relatedstudent__user=relatedstudent_user1).count(),
            1)
        self.assertEqual(
            Candidate.objects.filter(
                assignment_group__parentnode=created_assignment, relatedstudent__user=relatedstudent_user2).count(),
            1)

    def test_post_copy_all_students_from_another_assignment_same_group_structure(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        group1 = mommy.make('core.AssignmentGroup', parentnode=other_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=other_assignment, name='group2')
        relatedstudent_user1_group1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent_user2_group1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent_user_group2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', assignment_group=group1,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user1_group1)
        mommy.make('core.Candidate', assignment_group=group1,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user2_group1)
        mommy.make('core.Candidate', assignment_group=group2,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user_group2)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': '{}_all'.format(other_assignment.id)
                }
            })
        self.assertEqual(Assignment.objects.filter(short_name='testassignment').count(), 1)
        created_assignment = Assignment.objects.get(short_name='testassignment')
        self.assertEqual(created_assignment.assignmentgroups.count(), 2)
        self.assertEqual(Candidate.objects.filter(
            assignment_group__name='group1', assignment_group__parentnode=created_assignment).count(), 2)
        self.assertTrue(Candidate.objects.filter(
            assignment_group__name='group2',
            assignment_group__parentnode=created_assignment,
            relatedstudent__user=relatedstudent_user_group2).exists())
        self.assertTrue(Candidate.objects.filter(
            assignment_group__name='group2',
            assignment_group__parentnode=created_assignment,
            relatedstudent__user=relatedstudent_user_group2).exists())

        self.assertEqual(Candidate.objects.filter(
            assignment_group__name='group2', assignment_group__parentnode=created_assignment).count(), 1)
        self.assertTrue(Candidate.objects.filter(
            assignment_group__name='group2',
            assignment_group__parentnode=created_assignment,
            relatedstudent__user=relatedstudent_user_group2).exists())

    def test_post_copy_with_passing_grade_from_another_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        group_passed = mommy.make('core.AssignmentGroup', parentnode=other_assignment)
        group_failed = mommy.make('core.AssignmentGroup', parentnode=other_assignment)
        relatedstudent_user1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent_user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', assignment_group=group_passed,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user1)
        mommy.make('core.Candidate', assignment_group=group_failed,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            grading_points=1, group=group_passed)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            grading_points=0, group=group_failed)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': '{}_passed'.format(other_assignment.id)
                }
            })
        self.assertEqual(Assignment.objects.filter(short_name='testassignment').count(), 1)
        created_assignment = Assignment.objects.get(short_name='testassignment')
        self.assertEqual(created_assignment.assignmentgroups.count(), 1)
        self.assertEqual(Candidate.objects.filter(assignment_group__parentnode=created_assignment).count(), 1)
        self.assertTrue(
            Candidate.objects.filter(
                assignment_group__parentnode=created_assignment, relatedstudent__user=relatedstudent_user1).exists())

    def test_post_copy_with_passing_grade_from_another_assignment_same_group_structure(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        group = mommy.make('core.AssignmentGroup', parentnode=other_assignment)
        relatedstudent_user1 = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent_user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', assignment_group=group,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user1)
        mommy.make('core.Candidate', assignment_group=group,
                   relatedstudent__period=period, relatedstudent__user=relatedstudent_user2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            grading_points=1, group=group)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': '{}_passed'.format(other_assignment.id)
                }
            })
        self.assertEqual(Assignment.objects.filter(short_name='testassignment').count(), 1)
        created_assignment = Assignment.objects.get(short_name='testassignment')
        self.assertEqual(created_assignment.assignmentgroups.count(), 1)
        created_group = created_assignment.assignmentgroups.get()
        self.assertEqual(Candidate.objects.filter(assignment_group=created_group).count(), 2)
        self.assertTrue(
            Candidate.objects.filter(
                assignment_group=created_group, relatedstudent__user=relatedstudent_user1).exists())
        self.assertTrue(
            Candidate.objects.filter(
                assignment_group=created_group, relatedstudent__user=relatedstudent_user2).exists())

    def test_post_copy_with_passing_grade_from_another_examiners_copied(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        group = mommy.make('core.AssignmentGroup', parentnode=other_assignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            grading_points=1, group=group)
        self.mock_http302_postrequest(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'student_import_option': '{}_passed'.format(other_assignment.id)
                }
            })
        self.assertEqual(Assignment.objects.filter(short_name='testassignment').count(), 1)
        created_assignment = Assignment.objects.get(short_name='testassignment')
        self.assertEqual(created_assignment.assignmentgroups.count(), 1)
        self.assertEqual(Examiner.objects.filter(assignmentgroup__parentnode=created_assignment).count(), 1)

    def test_post_first_deadline_outside_period(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        first_deadline_isoformat = datetimeutils.isoformat_noseconds(FUTURE_PERIOD_END)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': first_deadline_isoformat,
                }
            })
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertTrue(mockresponse.selector.exists('#error_1_id_first_deadline'))
        self.assertIn('First deadline must be within',
                      mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized)

    def test_post_first_deadline_before_publishing_time_hours(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        first_deadline_isoformat = datetimeutils.isoformat_noseconds(timezone.now())
        with self.settings(DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES=60 * 3):
            mockresponse = self.mock_http200_postrequest_htmls(
                cradmin_role=period,
                requestkwargs={
                    'data': {
                        'long_name': 'Test assignment',
                        'short_name': 'testassignment',
                        'first_deadline': first_deadline_isoformat,
                    }
                })
            self.assertEqual(Assignment.objects.count(), 0)
            self.assertTrue(mockresponse.selector.exists('#error_1_id_first_deadline'))
            self.assertEqual('First deadline must be at least 3 hours from now.',
                             mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized)

    def test_post_first_deadline_before_publishing_time_minutes(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        first_deadline_isoformat = datetimeutils.isoformat_noseconds(timezone.now())
        with self.settings(DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES=30):
            mockresponse = self.mock_http200_postrequest_htmls(
                cradmin_role=period,
                requestkwargs={
                    'data': {
                        'long_name': 'Test assignment',
                        'short_name': 'testassignment',
                        'first_deadline': first_deadline_isoformat,
                    }
                })
            self.assertEqual(Assignment.objects.count(), 0)
            self.assertTrue(mockresponse.selector.exists('#error_1_id_first_deadline'))
            self.assertEqual('First deadline must be at least 30 minutes from now.',
                             mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized)

    def __valid_post_request(self, period=None, first_deadline=ACTIVE_PERIOD_END,
                             publishing_time_delay_minutes=60, student_import_option='all'):
        if not period:
            period = mommy.make_recipe('devilry.apps.core.period_active')
        with self.settings(DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES=publishing_time_delay_minutes):
            mockresponse = self.mock_http302_postrequest(
                cradmin_role=period,
                requestkwargs={
                    'data': {
                        'long_name': 'Test assignment',
                        'short_name': 'testassignment',
                        'first_deadline': datetimeutils.isoformat_noseconds(first_deadline),
                        'student_import_option': student_import_option
                    }
                })
        created_assignment = Assignment.objects.get(short_name='testassignment')
        return created_assignment, mockresponse

    def test_post_sanity(self):
        self.assertEqual(Assignment.objects.count(), 0)
        created_assignment, mockresponse = self.__valid_post_request(first_deadline=ACTIVE_PERIOD_END)
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertEqual(created_assignment.long_name, 'Test assignment')
        self.assertEqual(created_assignment.short_name, 'testassignment')
        self.assertEqual(
            ACTIVE_PERIOD_END,
            created_assignment.first_deadline)

    def test_post_success_redirect(self):
        self.assertEqual(Assignment.objects.count(), 0)
        created_assignment, mockresponse = self.__valid_post_request(first_deadline=ACTIVE_PERIOD_END)
        self.assertEqual(mockresponse.response['location'],
                         crinstance.reverse_cradmin_url(
                             instanceid='devilry_admin_assignmentadmin',
                             appname='overview',
                             roleid=created_assignment.id))

    def test_post_publishing_time(self):
        created_assignment, mockresponse = self.__valid_post_request(publishing_time_delay_minutes=60)
        self.assertTrue(
            (timezone.now() + timedelta(minutes=59)) <
            created_assignment.publishing_time <
            (timezone.now() + timedelta(minutes=61))
        )

    def test_post_future_period_sanity(self):
        self.assertEqual(Assignment.objects.count(), 0)
        period = mommy.make_recipe('devilry.apps.core.period_future')
        self.__valid_post_request(period=period, first_deadline=ASSIGNMENT_FUTUREPERIOD_START_FIRST_DEADLINE)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_post_future_publishing_time(self):
        period = mommy.make_recipe('devilry.apps.core.period_future')
        created_assignment, mockresponse = self.__valid_post_request(
            period=period,
            first_deadline=ASSIGNMENT_FUTUREPERIOD_START_FIRST_DEADLINE,
            publishing_time_delay_minutes=60
        )
        self.assertEqual(created_assignment.publishing_time, (period.start_time + timedelta(minutes=60)))

    def test_post_add_no_students(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.RelatedStudent', period=period,
                   user__shortname='student1')
        mommy.make('core.RelatedStudent', period=period,
                   user__shortname='student2')
        created_assignment, mockresponse = self.__valid_post_request(period=period, student_import_option='none')
        self.assertEqual(created_assignment.assignmentgroups.count(), 0)
        self.assertEqual(Candidate.objects.filter(assignment_group__parentnode=created_assignment).count(), 0)

    def test_post_add_all_relatedstudents_on_period(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.RelatedStudent', period=period,
                   user__shortname='student1')
        mommy.make('core.RelatedStudent', period=period,
                   user__shortname='student2')
        created_assignment, mockresponse = self.__valid_post_request(period=period)
        self.assertEqual(2, created_assignment.assignmentgroups.count())
        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=created_assignment)
        self.assertEqual(2, candidatesqueryset.count())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student1').exists())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student2').exists())

    def test_post_add_all_relatedstudents_on_period_no_students_on_period(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        created_assignment, mockresponse = self.__valid_post_request(period=period)
        self.assertEqual(0, created_assignment.assignmentgroups.count())
        self.assertEqual(Candidate.objects.filter(assignment_group__parentnode=created_assignment).count(), 0)

    def test_post_add_students_from_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        other_assignment = mommy.make('core.Assignment', parentnode=period)
        mommy.make('core.Candidate',
                   assignment_group__parentnode=other_assignment,
                   relatedstudent__period=period, _quantity=2)
        created_assignment, mockresponse = self.__valid_post_request(
            period=period, student_import_option='{}_all'.format(other_assignment.id))
        self.assertEqual(2, created_assignment.assignmentgroups.count())
        self.assertEqual(Candidate.objects.filter(assignment_group__parentnode=created_assignment).count(), 2)
