from django.conf import settings
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crinstance
from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_admin.views.dashboard import createsubject


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createsubject.CreateView

    def test_get_render_title(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=user)
        self.assertEqual('Create new course',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_get_render_h1(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=user)
        self.assertEqual('Create new course',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_get_render_formfields(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=user)
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))

    def test_post_missing_short_name(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=user,
            requestkwargs={
                'data': {
                    'long_name': 'Test subject',
                    'short_name': '',
                }
            })
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def test_post_missing_long_name(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=user,
            requestkwargs={
                'data': {
                    'long_name': '',
                    'short_name': 'testsubject'
                }
            })
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_long_name').alltext_normalized)

    def test_post_duplicate_short_name(self):
        user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=user,
            requestkwargs={
                'data': {
                    'long_name': 'Test subject',
                    'short_name': '',
                }
            })
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            'This field is required.',
            mockresponse.selector.one('#error_1_id_short_name').alltext_normalized)

    def __valid_post_request(self, user=None):
        if not user:
            user = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=user,
            requestkwargs={
                'data': {
                    'long_name': 'Test subject',
                    'short_name': 'testsubject',
                }
            })
        created_subject = Subject.objects.get(short_name='testsubject')
        return created_subject, mockresponse

    def test_post_sanity(self):
        self.assertEqual(Subject.objects.count(), 0)
        created_subject, mockresponse = self.__valid_post_request()
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual('Test subject', created_subject.long_name)
        self.assertEqual('testsubject', created_subject.short_name)

    def test_post_success_redirect(self):
        created_subject, mockresponse = self.__valid_post_request()
        self.assertEqual(mockresponse.response['location'],
                         crinstance.reverse_cradmin_url(
                             instanceid='devilry_admin_subjectadmin',
                             appname='overview',
                             roleid=created_subject.id))
