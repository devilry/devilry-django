import unittest

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import TestCase, RequestFactory
import htmls
import mock
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.tests.common.test_bulkimport_users_common import AbstractTypeInUsersViewTestMixin
from devilry.devilry_admin.views.period import examiners
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder2


@unittest.skip('Must be updated to listbuilder')
class TestListView(TestCase):
    def __mock_get_request(self, role, user):
        request = RequestFactory().get('/')
        request.user = user
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = examiners.ListView.as_view()(request)
        return response

    def mock_http200_getrequest_htmls(self, role, user):
        response = self.__mock_get_request(role=role, user=user)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def __get_shortnames(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-user-verbose-inline-shortname')]

    def __get_names(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-user-verbose-inline')]

    def test_title(self):
        testuser = UserBuilder2().user
        subjectbuilder = PeriodBuilder.make(long_name='The Long Name') \
            .add_relatedexaminers(testuser)
        selector = self.mock_http200_getrequest_htmls(role=subjectbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('title').alltext_normalized,
                         'Examiners')

    def test_no_examiners_messages(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make()
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('#objecttableview-no-items-message').alltext_normalized,
                         'There is no examiners registered for {}.'.format(
                             periodbuilder.get_object().get_path()))

    def test_ordering(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='userb').user,
                                  UserBuilder2(shortname='usera').user,
                                  UserBuilder2(shortname='userc').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(['usera', 'userb', 'userc'], self.__get_shortnames(selector))

    def test_render_user_with_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test', fullname='Test User').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(['Test User(test)'], self.__get_names(selector))

    def test_render_user_without_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(['test'], self.__get_names(selector))

    def test_render_email_has_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').add_primary_email('test@example.com').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('.devilry-admin-adminlist-email').alltext_normalized,
                         'Contact at test@example.com')
        self.assertEqual(selector.one('.devilry-admin-adminlist-email')['href'],
                         'mailto:test@example.com')

    def test_render_email_no_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('.devilry-admin-adminlist-email')),

    def test_render_only_users_from_current_basenode(self):
        testuser = UserBuilder2(is_superuser=True).user
        PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='otherbasenodeuser').user)
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='expecteduser').user)
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(['expecteduser'], self.__get_names(selector))


class TestRemoveExaminerView(TestCase):
    def __mock_request(self, method, role, requestuser, user_to_remove,
                       messagesmock=None):
        request = getattr(RequestFactory(), method)('/')
        request.user = requestuser
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        if messagesmock:
            request._messages = messagesmock
        else:
            request._messages = mock.MagicMock()
        admin_to_remove = RelatedExaminer.objects.get(user=user_to_remove)
        response = examiners.RemoveView.as_view()(request, pk=admin_to_remove.pk)
        return response

    def __mock_http200_getrequest_htmls(self, role, requestuser, user_to_remove):
        response = self.__mock_request(method='get',
                                       role=role,
                                       requestuser=requestuser,
                                       user_to_remove=user_to_remove)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def __mock_postrequest(self, role, requestuser, user_to_remove, messagesmock=None):
        response = self.__mock_request(method='post',
                                       role=role,
                                       requestuser=requestuser,
                                       user_to_remove=user_to_remove,
                                       messagesmock=messagesmock)
        return response

    def test_get(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode') \
            .add_relatedexaminers(requestuser, janedoe)
        selector = self.__mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                        requestuser=requestuser,
                                                        user_to_remove=janedoe)
        self.assertEqual(selector.one('title').alltext_normalized,
                         'Remove Jane Doe')
        self.assertEqual(selector.one('#deleteview-preview').alltext_normalized,
                         'Are you sure you want to remove Jane Doe '
                         'as examiner for {}?'.format(periodbuilder.get_object()))

    def test_post_remove_yourself_404(self):
        requestuser = UserBuilder2().user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(requestuser)
        with self.assertRaises(Http404):
            self.__mock_postrequest(role=periodbuilder.get_object(),
                                    requestuser=requestuser,
                                    user_to_remove=requestuser)

    def test_post_remove_yourself_superuser_ok(self):
        requestuser = UserBuilder2(is_superuser=True).user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(requestuser)
        response = self.__mock_postrequest(role=periodbuilder.get_object(),
                                           requestuser=requestuser,
                                           user_to_remove=requestuser)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(pk=requestuser.pk).exists())
        self.assertFalse(periodbuilder.get_object().relatedexaminer_set.filter(pk=requestuser.pk).exists())

    def test_post_remove_ok(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode') \
            .add_relatedexaminers(requestuser, janedoe)
        messagesmock = mock.MagicMock()
        response = self.__mock_postrequest(role=periodbuilder.get_object(),
                                           requestuser=requestuser,
                                           user_to_remove=janedoe,
                                           messagesmock=messagesmock)
        self.assertEqual(response.status_code, 302)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe is no longer examiner for {}.'.format(periodbuilder.get_object()),
            '')
        self.assertTrue(get_user_model().objects.filter(pk=janedoe.pk).exists())
        self.assertFalse(periodbuilder.get_object().relatedexaminer_set.filter(pk=janedoe.pk).exists())


class TestUserSelectView(TestCase):
    def __mock_get_request(self, role, user):
        request = RequestFactory().get('/')
        request.user = user
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = examiners.UserSelectView.as_view()(request)
        return response

    def mock_http200_getrequest_htmls(self, role, user):
        response = self.__mock_get_request(role=role, user=user)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_render(self):
        testuser = UserBuilder2().user
        periodbuilder = PeriodBuilder.make() \
            .add_relatedexaminers(testuser)  # testuser should be excluded since it is already examiner
        UserBuilder2(shortname='Jane Doe')
        selector = self.mock_http200_getrequest_htmls(role=periodbuilder.get_object(),
                                                      user=testuser)
        self.assertTrue(selector.exists(
            '#objecttableview-table tbody .devilry-admin-userselect-select-button'))
        self.assertEqual(
            selector.one('#objecttableview-table tbody '
                         '.devilry-admin-userselect-select-button').alltext_normalized,
            'Add as examiner')


class TestAddView(TestCase):
    def __mock_postrequest(self, role, requestuser, data, messagesmock=None):
        request = RequestFactory().post('/', data=data)
        request.user = requestuser
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        if messagesmock:
            request._messages = messagesmock
        else:
            request._messages = mock.MagicMock()
        response = examiners.AddView.as_view()(request)
        return response, request

    def test_invalid_user(self):
        requestuser = UserBuilder2().user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode')
        response, request = self.__mock_postrequest(role=periodbuilder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': 10000000001})
        self.assertEqual(response.status_code, 302)
        request._messages.add.assert_called_once_with(
            messages.ERROR,
            'Error: The user may not exist, or it may already be examiner.', '')
        request.cradmin_app.reverse_appindexurl.assert_called_once()

    def test_user_already_examiner(self):
        # Just to ensure the ID of the RelatedExaminer does not match
        # the ID of the User
        UserBuilder2()
        UserBuilder2()
        requestuser = UserBuilder2().user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode') \
            .add_relatedexaminers(requestuser)
        response, request = self.__mock_postrequest(role=periodbuilder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': requestuser.id})
        self.assertEqual(response.status_code, 302)
        request._messages.add.assert_called_once_with(
            messages.ERROR,
            'Error: The user may not exist, or it may already be examiner.', '')
        request.cradmin_app.reverse_appindexurl.assert_called_once()

    def test_adds_user_to_relatedexaminers(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2().user
        periodbuilder = PeriodBuilder.make()
        self.assertFalse(periodbuilder.get_object().relatedexaminer_set.filter(user=janedoe).exists())
        self.__mock_postrequest(role=periodbuilder.get_object(),
                                requestuser=requestuser,
                                data={'user': janedoe.id})
        self.assertTrue(periodbuilder.get_object().relatedexaminer_set.filter(user=janedoe).exists())

    def test_success_message(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode')
        response, request = self.__mock_postrequest(role=periodbuilder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id})
        request._messages.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe added as examiner for {}.'.format(periodbuilder.get_object()),
            '')

    def test_success_redirect_without_next(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode')
        response, request = self.__mock_postrequest(role=periodbuilder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id})
        self.assertEqual(response.status_code, 302)
        request.cradmin_app.reverse_appindexurl.assert_called_once()

    def test_success_redirect_with_next(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        periodbuilder = PeriodBuilder.make(short_name='testbasenode')
        response, request = self.__mock_postrequest(role=periodbuilder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id,
                                                          'next': '/next'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/next')


class TestBulkImportView(TestCase, AbstractTypeInUsersViewTestMixin):
    viewclass = examiners.BulkImportView

    def test_post_valid_with_email_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs=dict(data={
                    'users_blob': 'test1@example.com\ntest2@example.com'
                })
            )
            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual({'test1@example.com', 'test2@example.com'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in RelatedExaminer.objects.all()})

    def test_post_valid_with_email_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test1@example.com\ntest2@example.com'
                })
            )
            messagesmock.add.assert_any_call(
                messages.SUCCESS,
                'Added 2 new examiners to {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_email_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_emails('test@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test@example.com'
                })
            )
            messagesmock.add.assert_any_call(
                messages.WARNING,
                'No new examiners was added.',
                '')

    def test_post_valid_with_email_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_emails('test@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test@example.com'
                })
            )
            messagesmock.add.assert_called_with(
                messages.INFO,
                '1 users was already examiner on {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_username_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs=dict(data={
                    'users_blob': 'test1\ntest2'
                })
            )
            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual({'test1', 'test2'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in RelatedExaminer.objects.all()})

    def test_post_valid_with_username_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test1\ntest2'
                })
            )
            messagesmock.add.assert_any_call(
                messages.SUCCESS,
                'Added 2 new examiners to {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_username_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_usernames('test').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test'
                })
            )
            messagesmock.add.assert_any_call(
                messages.WARNING,
                'No new examiners was added.',
                '')

    def test_post_valid_with_username_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_usernames('test').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test'
                })
            )
            messagesmock.add.assert_any_call(
                messages.INFO,
                '1 users was already examiner on {}.'.format(testperiod.get_path()),
                '')
