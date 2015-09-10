from datetime import datetime, timedelta
from django.template import defaultfilters
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.period import createassignment
from devilry.project.develop.testhelpers import corebuilder
from devilry.utils import datetimeutils


class TestNameSuggestion(TestCase):
    def test_number_no_number(self):
        self.assertEqual(createassignment.NameSuggestion(long_name='Test', short_name='test').number, None)

    def test_number_not_the_same_number(self):
        self.assertEqual(createassignment.NameSuggestion(long_name='Test1', short_name='test2').number, None)

    def test_number_number_in_the_middle(self):
        self.assertEqual(
            createassignment.NameSuggestion(long_name='Test 1 assignment', short_name='test1assignment').number,
            None)

    def test_number_suffixed_with_number(self):
        self.assertEqual(createassignment.NameSuggestion(long_name='Test1', short_name='test1').number, 1)

    def test_number_suffixed_with_number_zero(self):
        # Ensure we do not have any ``if not number``, which would
        # evaluate to no match for ``0``.
        self.assertEqual(createassignment.NameSuggestion(long_name='Test0', short_name='test0').number, 0)

    def test_number_suffixed_multicharacter_number(self):
        self.assertEqual(createassignment.NameSuggestion(long_name='Test2001', short_name='test2001').number, 2001)

    def test_create_names_from_number_no_number(self):
        namesuggestion = createassignment.NameSuggestion(long_name='Test', short_name='test')
        self.assertEqual(namesuggestion.suggested_long_name, '')
        self.assertEqual(namesuggestion.suggested_short_name, '')

    def test_create_names_from_number(self):
        namesuggestion = createassignment.NameSuggestion(long_name='Test 1', short_name='test1')
        self.assertEqual(namesuggestion.suggested_long_name, 'Test 2')
        self.assertEqual(namesuggestion.suggested_short_name, 'test2')

    def test_has_suggestion_false(self):
        namesuggestion = createassignment.NameSuggestion(long_name='Test', short_name='test')
        self.assertFalse(namesuggestion.has_suggestion())

    def test_has_suggestion_true(self):
        namesuggestion = createassignment.NameSuggestion(long_name='Test 1', short_name='test1')
        self.assertTrue(namesuggestion.has_suggestion())


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createassignment.CreateView

    def test_get_render_formfields(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=first_deadline]'))

    def test_get_suggested_name_first_assignment(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_not_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder\
            .make(long_name='Test', short_name='test').assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_suffixed_with_number(self):
        testperiod = corebuilder.AssignmentBuilder\
            .make(long_name='Test1', short_name='test1',
                  first_deadline=timezone.now())\
            .assignment.period
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), 'Test2')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), 'test2')

    def test_get_suggested_name_previous_assignment_suffixed_with_number_namecollision_no_first_deadline(self):
        testperiod = corebuilder.PeriodBuilder.make().period
        corebuilder.AssignmentBuilder\
            .make(long_name='Test1', short_name='test1',
                  first_deadline=timezone.now(),
                  period=testperiod)
        corebuilder.AssignmentBuilder\
            .make(long_name='Test2', short_name='test2',
                  first_deadline=None,
                  period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_assignment_suffixed_with_number_namecollision_strange_order(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        periodbuilder.add_assignment(long_name='Test1', short_name='test1',
                                     first_deadline=timezone.now())
        periodbuilder.add_assignment(long_name='Test2', short_name='test2',
                                     first_deadline=timezone.now() - timedelta(days=30))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=periodbuilder.period)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

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

    def __get_valid_first_deadline_isoformatted(self):
        return datetimeutils.isoformat_noseconds(
            timezone.now() + timedelta(days=10))

    def test_post_ok(self):
        periodbuilder = corebuilder.PeriodBuilder.make()
        self.assertEqual(Assignment.objects.count(), 0)
        first_deadline_isoformat = self.__get_valid_first_deadline_isoformatted()
        self.mock_http302_postrequest(
            cradmin_role=periodbuilder.period,
            requestkwargs={
                'data': {
                    'long_name': 'Test assignment',
                    'short_name': 'testassignment',
                    'first_deadline': first_deadline_isoformat,
                }
            })
        self.assertEqual(Assignment.objects.count(), 1)
        created_assignment = Assignment.objects.first()
        self.assertEqual(created_assignment.long_name, 'Test assignment')
        self.assertEqual(created_assignment.short_name, 'testassignment')
        self.assertEqual(
            first_deadline_isoformat,
            datetimeutils.isoformat_noseconds(created_assignment.first_deadline))

    # def test_post_first_deadline_before_preferred_publishing_time(self):
    #     periodbuilder = corebuilder.PeriodBuilder.make()
    #     self.assertEqual(Assignment.objects.count(), 0)
    #     first_deadline_isoformat = datetimeutils.isoformat_noseconds(timezone.now())
    #     mockresponse = self.mock_http200_postrequest_htmls(
    #         cradmin_role=periodbuilder.period,
    #         requestkwargs={
    #             'data': {
    #                 'long_name': 'Test assignment',
    #                 'short_name': 'testassignment',
    #                 'first_deadline': first_deadline_isoformat,
    #             }
    #         })
