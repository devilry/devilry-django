from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory
import htmls
import mock

from devilry.project.develop.testhelpers.corebuilder import UserBuilder2


class AdminsListViewTestMixin(object):
    builderclass = None
    viewclass = None

    def __mock_get_request(self, role, user):
        request = RequestFactory().get('/')
        request.user = user
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = self.viewclass.as_view()(request)
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
        subjectbuilder = self.builderclass.make(long_name='The Long Name') \
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=subjectbuilder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('title').alltext_normalized,
                         'Administrators for The Long Name')

    def test_remove_not_shown_for_requesting_user(self):
        testuser = UserBuilder2().user
        builder = self.builderclass.make() \
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_remove_shown_for_requesting_user_if_superuser(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertTrue(selector.exists(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_remove_shown_other_than_requesting_user(self):
        testuser = UserBuilder2().user
        builder = self.builderclass.make() \
            .add_admins(testuser, UserBuilder2(shortname='other').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(1, selector.count(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_no_admins_messages(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make()
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('#objecttableview-no-items-message').alltext_normalized,
                         'There is no administrators registered for {}.'.format(
                             builder.get_object().get_path()))

    def test_ordering(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='userb').user,
                        UserBuilder2(shortname='usera').user,
                        UserBuilder2(shortname='userc').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['usera', 'userb', 'userc'], self.__get_shortnames(selector))

    def test_render_user_with_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='test', fullname='Test User').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['Test User(test)'], self.__get_names(selector))

    def test_render_user_without_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['test'], self.__get_names(selector))

    def test_render_email_has_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='test').add_primary_email('test@example.com').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('.devilry-admin-adminlist-email').alltext_normalized,
                         'Contact at test@example.com')
        self.assertEqual(selector.one('.devilry-admin-adminlist-email')['href'],
                         'mailto:test@example.com')

    def test_render_email_no_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('.devilry-admin-adminlist-email')),

    def test_render_only_users_from_current_basenode(self):
        testuser = UserBuilder2(is_superuser=True).user
        self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='otherbasenodeuser').user)
        builder = self.builderclass.make() \
            .add_admins(UserBuilder2(shortname='expecteduser').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['expecteduser'], self.__get_names(selector))


class RemoveAdminViewTestMixin(object):
    builderclass = None
    viewclass = None

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
        admin_to_remove = self.builderclass.modelcls.admins.through.objects.get(user=user_to_remove)
        response = self.viewclass.as_view()(request, pk=admin_to_remove.pk)
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
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser, janedoe)
        selector = self.__mock_http200_getrequest_htmls(role=builder.get_object(),
                                                        requestuser=requestuser,
                                                        user_to_remove=janedoe)
        self.assertEqual(selector.one('title').alltext_normalized,
                         'Remove Jane Doe')
        self.assertEqual(selector.one('#deleteview-preview').alltext_normalized,
                         'Are you sure you want to remove Jane Doe '
                         'as administrator for {}?'.format(builder.get_object()))

    def test_post_remove_yourself_404(self):
        requestuser = UserBuilder2().user
        builder = self.builderclass.make() \
            .add_admins(requestuser)
        with self.assertRaises(Http404):
            self.__mock_postrequest(role=builder.get_object(),
                                    requestuser=requestuser,
                                    user_to_remove=requestuser)

    def test_post_remove_yourself_superuser_ok(self):
        requestuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make() \
            .add_admins(requestuser)
        response = self.__mock_postrequest(role=builder.get_object(),
                                           requestuser=requestuser,
                                           user_to_remove=requestuser)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(pk=requestuser.pk).exists())
        self.assertFalse(builder.get_object().admins.filter(pk=requestuser.pk).exists())

    def test_post_remove_ok(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser, janedoe)
        messagesmock = mock.MagicMock()
        response = self.__mock_postrequest(role=builder.get_object(),
                                           requestuser=requestuser,
                                           user_to_remove=janedoe,
                                           messagesmock=messagesmock)
        self.assertEqual(response.status_code, 302)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe is no longer administrator for {}.'.format(builder.get_object()),
            '')
        self.assertTrue(get_user_model().objects.filter(pk=janedoe.pk).exists())
        self.assertFalse(builder.get_object().admins.filter(pk=janedoe.pk).exists())


class AdminUserSelectViewTestMixin(object):
    builderclass = None
    viewclass = None

    def __mock_get_request(self, role, user):
        request = RequestFactory().get('/')
        request.user = user
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = self.viewclass.as_view()(request)
        return response

    def mock_http200_getrequest_htmls(self, role, user):
        response = self.__mock_get_request(role=role, user=user)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_render(self):
        testuser = UserBuilder2().user
        builder = self.builderclass.make() \
            .add_admins(testuser)  # testuser should be excluded since it is already admin
        UserBuilder2(shortname='Jane Doe')
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertTrue(selector.exists(
            '#objecttableview-table tbody .devilry-admin-userselect-select-button'))
        self.assertEqual(
            selector.one('#objecttableview-table tbody '
                         '.devilry-admin-userselect-select-button').alltext_normalized,
            'Add as administrator')


class AddAdminViewTestMixin(object):
    builderclass = None
    viewclass = None

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
        response = self.viewclass.as_view()(request)
        return response, request

    def test_invalid_user(self):
        requestuser = UserBuilder2().user
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser)
        response, request = self.__mock_postrequest(role=builder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': 10000000001})
        self.assertEqual(response.status_code, 302)
        request._messages.add.assert_called_once_with(
            messages.ERROR,
            'Error: The user may not exist, or it may already be administrator.', '')
        request.cradmin_app.reverse_appindexurl.assert_called_once()

    def test_adds_user_to_admins(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2().user
        builder = self.builderclass.make() \
            .add_admins(requestuser)
        self.assertFalse(builder.get_object().admins.filter(pk=janedoe.pk).exists())
        self.__mock_postrequest(role=builder.get_object(),
                                requestuser=requestuser,
                                data={'user': janedoe.id})
        self.assertTrue(builder.get_object().admins.filter(pk=janedoe.pk).exists())

    def test_success_message(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser)
        response, request = self.__mock_postrequest(role=builder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id})
        request._messages.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe added as administrator for {}.'.format(builder.get_object()),
            '')

    def test_success_redirect_without_next(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser)
        response, request = self.__mock_postrequest(role=builder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id})
        self.assertEqual(response.status_code, 302)
        request.cradmin_app.reverse_appindexurl.assert_called_once()

    def test_success_redirect_with_next(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        builder = self.builderclass.make(short_name='testbasenode') \
            .add_admins(requestuser)
        response, request = self.__mock_postrequest(role=builder.get_object(),
                                                    requestuser=requestuser,
                                                    data={'user': janedoe.id,
                                                          'next': '/next'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/next')
