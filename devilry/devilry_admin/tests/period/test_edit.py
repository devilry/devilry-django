import mock
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Period
from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_END, ACTIVE_PERIOD_START
from devilry.devilry_admin.views.period import edit
from devilry.utils import datetimeutils


class TestUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = edit.UpdateView

    def test_get_render_title(self):
        testperiod = baker.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertIn('Edit testsubject.testperiod',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_get_render_h1(self):
        testperiod = baker.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual('Edit testsubject.testperiod',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_get_render_formfields(self):
        testperiod = baker.make('core.Period',
                                long_name='Test period',
                                short_name='testperiod',
                                start_time=ACTIVE_PERIOD_START,
                                end_time=ACTIVE_PERIOD_END)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod)
        self.assertEqual(
                'Test period',
                mockresponse.selector.one('input[name=long_name]')['value'])
        self.assertEqual(
                'testperiod',
                mockresponse.selector.one('input[name=short_name]')['value'])
        self.assertEqual(
                datetimeutils.isoformat_withseconds(ACTIVE_PERIOD_START),
                mockresponse.selector.one('input[name=start_time]')['value'])
        self.assertEqual(
                datetimeutils.isoformat_withseconds(ACTIVE_PERIOD_END),
                mockresponse.selector.one('input[name=end_time]')['value'])

    def test_post_missing_short_name(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': '',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def test_post_missing_long_name(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': '',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_long_name').alltext_normalized)

    def test_post_missing_start_time(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': '',
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_start_time').alltext_normalized)

    def test_post_missing_end_time(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                    'end_time': '',
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_end_time').alltext_normalized)

    def test_post_start_time_before_end_time(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                    'end_time': datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                }
            })
        self.assertEqual(
            'Start time must be before end time.',
            mockresponse.selector.one('.alert-danger').alltext_normalized)

    def __valid_post_request(self, testperiod,
                             start_time=ACTIVE_PERIOD_START,
                             end_time=ACTIVE_PERIOD_END,
                             **kwargs):
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'long_name': 'Test period',
                    'short_name': 'testperiod',
                    'start_time': datetimeutils.isoformat_noseconds(start_time),
                    'end_time': datetimeutils.isoformat_noseconds(end_time),
                }
            },
            **kwargs)
        updated_period = Period.objects.get(id=testperiod.id)
        return updated_period, mockresponse

    def test_post_sanity(self):
        testperiod = baker.make('core.Period')
        updated_period, mockresponse = self.__valid_post_request(
                testperiod=testperiod,
                start_time=ACTIVE_PERIOD_START,
                end_time=ACTIVE_PERIOD_END)
        self.assertEqual(Period.objects.count(), 1)
        self.assertEqual('Test period', updated_period.long_name)
        self.assertEqual('testperiod', updated_period.short_name)
        self.assertEqual(ACTIVE_PERIOD_START, updated_period.start_time)
        self.assertEqual(ACTIVE_PERIOD_END, updated_period.end_time)

    def test_post_success_redirect(self):
        testperiod = baker.make('core.Period')
        mock_cradmin_instance = mock.MagicMock()
        self.__valid_post_request(
                testperiod=testperiod,
                cradmin_instance=mock_cradmin_instance)
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with()
