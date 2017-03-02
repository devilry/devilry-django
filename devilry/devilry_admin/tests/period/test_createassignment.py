from datetime import datetime, timedelta

import unittest

from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
import mock
from model_mommy import mommy
from django_cradmin import crinstance

from devilry.apps.core.models import Assignment, Candidate, Examiner
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_END, ACTIVE_PERIOD_START, OLD_PERIOD_START, FUTURE_PERIOD_END
from devilry.devilry_admin.views.period import createassignment
from devilry.utils import datetimeutils


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createassignment.CreateView

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
                          first_deadline=datetime(2015, 9, 2, 13, 30))  # Wed

        timezonemock = mock.MagicMock()
        timezonemock.now.return_value = datetime(2015, 9, 10, 22, 18)  # Thursday
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
                          first_deadline=datetime(3500, 9, 5, 13, 30))

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
                          first_deadline=datetime(3500, 9, 5, 13, 30))

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
                             publishing_time_delay_minutes=60):
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

    def test_post_first_assignment_adds_relatedstudents(self):
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

    def test_post_first_assignment_adds_examiners_from_syncsystem_tags(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        testperiodtag1 = mommy.make('core.PeriodTag', period=period, tag='group1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=period, tag='group2')
        testperiodtag1.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=period))
        testperiodtag1.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=period, user__shortname='examiner1'),
            mommy.make('core.RelatedExaminer', period=period, user__shortname='examiner2'))
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=period, user__shortname='examiner3'))
        testperiodtag_other = mommy.make('core.PeriodTag', tag='group2')
        testperiodtag_other.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', user__shortname='otherperiodexaminer'))

        created_assignment, mockresponse = self.__valid_post_request(period=period)
        self.assertEqual(1, created_assignment.assignmentgroups.count())
        created_group = created_assignment.assignmentgroups.first()
        self.assertTrue(created_group.examiners.filter(relatedexaminer__user__shortname='examiner1').exists())
        self.assertTrue(created_group.examiners.filter(relatedexaminer__user__shortname='examiner2').exists())
        self.assertFalse(created_group.examiners.filter(relatedexaminer__user__shortname='examiner3').exists())
        self.assertFalse(created_group.examiners.filter(relatedexaminer__user__shortname='otherperiodexaminer').exists())

    def test_post_second_assignment_copies_setup_from_first_assignment(self):
        period = mommy.make_recipe('devilry.apps.core.period_active')
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        parentnode=period)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        mommy.make('core.Candidate',
                   assignment_group=group,
                   relatedstudent__user__shortname='student1')
        mommy.make('core.Examiner',
                   assignmentgroup=group,
                   relatedexaminer__user__shortname='examiner1')

        created_assignment, mockresponse = self.__valid_post_request(period=period)
        self.assertEqual(1, created_assignment.assignmentgroups.count())

        candidatesqueryset = Candidate.objects.filter(assignment_group__parentnode=created_assignment)
        self.assertEqual(1, candidatesqueryset.count())
        self.assertTrue(candidatesqueryset.filter(relatedstudent__user__shortname='student1').exists())

        examinersqueryset = Examiner.objects.filter(assignmentgroup__parentnode=created_assignment)
        self.assertEqual(1, examinersqueryset.count())
        self.assertTrue(examinersqueryset.filter(relatedexaminer__user__shortname='examiner1').exists())
