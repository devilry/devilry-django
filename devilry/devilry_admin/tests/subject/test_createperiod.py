from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from django_cradmin import crinstance

from devilry.apps.core.models import Period
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_END, ACTIVE_PERIOD_START
from devilry.devilry_admin.views.subject import createperiod
from devilry.utils import datetimeutils


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createperiod.CreateView

    def test_get_render_title(self):
        subject = mommy.make('core.Subject', short_name='testcourse')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual('Create new semester - testcourse',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_get_render_h1(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual('Create new semester',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_get_render_formfields(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=start_time]'))
        self.assertTrue(mockresponse.selector.exists('input[name=end_time]'))

    def test_get_suggested_name_first_period(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_period_not_suffixed_with_number(self):
        subject = mommy.make_recipe('devilry.apps.core.period_old',
                                    long_name='Test', short_name='test').subject
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_get_suggested_name_previous_period_suffixed_with_number(self):
        subject = mommy.make_recipe('devilry.apps.core.period_old',
                                    long_name='Test1', short_name='test1').subject
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), 'Test2')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), 'test2')

    def test_get_suggested_name_previous_period_suffixed_with_number_namecollision_strange_order(self):
        subject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=subject,
                          long_name='Test1', short_name='test1')
        mommy.make_recipe('devilry.apps.core.period_old',
                          parentnode=subject,
                          long_name='Test2', short_name='test2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=subject)
        self.assertEqual(mockresponse.selector.one('input[name=long_name]').get('value', ''), '')
        self.assertEqual(mockresponse.selector.one('input[name=short_name]').get('value', ''), '')

    def test_post_missing_short_name(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': '',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def test_post_missing_long_name(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': '',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_long_name').alltext_normalized)

    def test_post_missing_start_time(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': '',
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_start_time').alltext_normalized)

    def test_post_missing_end_time(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': '',
                }
            })
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_end_time').alltext_normalized)

    def test_post_start_time_before_end_time(self):
        subject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                }
            })
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(
            'Start time must be before end time.',
            mockresponse.selector.one('.alert-danger').alltext_normalized)

    def __valid_post_request(self, subject=None,
                             start_time=ACTIVE_PERIOD_START,
                             end_time=ACTIVE_PERIOD_END):
        if not subject:
            subject = mommy.make('core.Subject')
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=subject,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(start_time),
                    'end_time': datetimeutils.isoformat_noseconds(end_time),
                }
            })
        created_period = Period.objects.get(short_name='testperiod')
        return created_period, mockresponse

    def test_post_sanity(self):
        self.assertEqual(Period.objects.count(), 0)
        created_period, mockresponse = self.__valid_post_request(start_time=ACTIVE_PERIOD_START,
                                                                 end_time=ACTIVE_PERIOD_END)
        self.assertEqual(Period.objects.count(), 1)
        self.assertEqual('Test period', created_period.long_name)
        self.assertEqual('testperiod', created_period.short_name)
        self.assertEqual(ACTIVE_PERIOD_START, created_period.start_time)
        self.assertEqual(ACTIVE_PERIOD_END, created_period.end_time)

    def test_post_success_redirect(self):
        self.assertEqual(Period.objects.count(), 0)
        created_period, mockresponse = self.__valid_post_request()
        self.assertEqual(mockresponse.response['location'],
                         crinstance.reverse_cradmin_url(
                             instanceid='devilry_admin_periodadmin',
                             appname='overview',
                             roleid=created_period.id))
