import mock
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_admin.views.subject import edit


class TestUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = edit.UpdateView

    def test_get_render_title(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testsubject)
        self.assertIn('Edit testsubject',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_get_render_h1(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testsubject)
        self.assertEqual('Edit testsubject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_get_render_formfields(self):
        testsubject = baker.make('core.Subject',
                                 long_name='Test subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testsubject)
        self.assertEqual(
                'Test subject',
                mockresponse.selector.one('input[name=long_name]')['value'])
        self.assertEqual(
                'testsubject',
                mockresponse.selector.one('input[name=short_name]')['value'])

    def test_post_missing_short_name(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testsubject,
            requestkwargs={
                'data': {
                    'long_name': 'Test subject',
                    'short_name': '',
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def test_post_missing_long_name(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testsubject,
            requestkwargs={
                'data': {
                    'long_name': '',
                    'short_name': 'testsubject',
                }
            })
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_long_name').alltext_normalized)

    def __valid_post_request(self, testsubject,
                             **kwargs):
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testsubject,
            requestkwargs={
                'data': {
                    'long_name': 'Test subject',
                    'short_name': 'testsubject',
                }
            },
            **kwargs)
        updated_period = Subject.objects.get(id=testsubject.id)
        return updated_period, mockresponse

    def test_post_sanity(self):
        testsubject = baker.make('core.Subject')
        updated_period, mockresponse = self.__valid_post_request(
                testsubject=testsubject)
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual('Test subject', updated_period.long_name)
        self.assertEqual('testsubject', updated_period.short_name)

    def test_post_success_redirect(self):
        testsubject = baker.make('core.Subject')
        mock_cradmin_instance = mock.MagicMock()
        self.__valid_post_request(
                testsubject=testsubject,
                cradmin_instance=mock_cradmin_instance)
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with()
