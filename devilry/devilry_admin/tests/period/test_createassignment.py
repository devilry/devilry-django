from datetime import datetime, timedelta
from django.template import defaultfilters
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from devilry.devilry_admin.views.period import createassignment
from devilry.project.develop.testhelpers import corebuilder


class TestCreateSuggestedName(TestCase):
    def test_no_number(self):
        self.assertEqual(createassignment.create_suggested_name('test'), '')

    def test_number_in_the_middle(self):
        self.assertEqual(createassignment.create_suggested_name('Assignment 10 test'), '')

    def test_suffixed_with_number(self):
        self.assertEqual(createassignment.create_suggested_name('test10'), 'test11')


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createassignment.CreateView

    def test_get_render_formfields(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=first_deadline]'))

    def test_get_suggested_assignment_long_name_first_assignment(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')

    def test_get_suggested_assignment_long_name_previous_assignment_not_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder.make(long_name='Test').assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')

    def test_get_suggested_assignment_long_name_previous_assignment_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder.make(
            long_name='Test1', first_deadline=timezone.now()).assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), 'Test2')

    def test_get_suggested_assignment_short_name_first_assignment(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_assignment_short_name_previous_assignment_not_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder.make(short_name='Test').assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_assignment_short_name_previous_assignment_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder.make(
            short_name='test1', first_deadline=timezone.now()).assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), 'test2')

    def test_get_suggested_deadlines_first_assignment(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertFalse(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    def test_get_suggested_deadlines_not_first_assignment(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        periodbuilder.add_assignment(
            publishing_time=datetime(2015, 1, 1),
            first_deadline=datetime(2015, 2, 1, 12, 30),
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=periodbuilder.period)
        self.assertTrue(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    def test_get_suggested_deadlines_not_first_assignment_no_previus_with_deadline(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        periodbuilder.add_assignment(
            publishing_time=datetime(2015, 1, 1),
            first_deadline=None)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=periodbuilder.period)
        self.assertFalse(mockresponse.selector.exists(
            '#devilry_admin_createassignment_suggested_deadlines'))

    def test_get_suggested_deadlines_render_values(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        periodbuilder.add_assignment(
            publishing_time=datetime(2015, 1, 1),
            first_deadline=datetime(2015, 2, 1),
        )
        periodbuilder.add_assignment(  # This should be the one that is used for suggestions
            publishing_time=datetime(2015, 1, 1),
            first_deadline=datetime(2015, 3, 1, 12, 30),
        )

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=periodbuilder.period)
        suggested_deadline_elements = mockresponse.selector.list(
            '.devilry-admin-createassignment-suggested-deadline')
        suggested_deadline_values = [element['django-cradmin-setfieldvalue']
                                     for element in suggested_deadline_elements]
        self.assertEqual(suggested_deadline_values, [
            (datetime(2015, 3, 1, 12, 30) + timedelta(days=7)).isoformat(),
            (datetime(2015, 3, 1, 12, 30) + timedelta(days=14)).isoformat(),
            (datetime(2015, 3, 1, 12, 30) + timedelta(days=21)).isoformat(),
            (datetime(2015, 3, 1, 12, 30) + timedelta(days=28)).isoformat(),
        ])

    def test_get_suggested_deadlines_render_labels(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        periodbuilder.add_assignment(
            publishing_time=datetime(2015, 1, 1),
            first_deadline=datetime(2015, 2, 1),
        )
        periodbuilder.add_assignment(  # This should be the one that is used for suggestions
            publishing_time=datetime(2015, 1, 1),
            first_deadline=datetime(2015, 3, 1, 12, 30),
        )

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=periodbuilder.period)
        suggested_deadline_elements = mockresponse.selector.list(
            '.devilry-admin-createassignment-suggested-deadline')
        suggested_deadline_labels = [element.alltext_normalized
                                     for element in suggested_deadline_elements]
        self.assertEqual(suggested_deadline_labels, [
            defaultfilters.date(datetime(2015, 3, 1, 12, 30) + timedelta(days=7),
                                'DATETIME_FORMAT'),
            defaultfilters.date(datetime(2015, 3, 1, 12, 30) + timedelta(days=14),
                                'DATETIME_FORMAT'),
            defaultfilters.date(datetime(2015, 3, 1, 12, 30) + timedelta(days=21),
                                'DATETIME_FORMAT'),
            defaultfilters.date(datetime(2015, 3, 1, 12, 30) + timedelta(days=28),
                                'DATETIME_FORMAT'),
        ])
