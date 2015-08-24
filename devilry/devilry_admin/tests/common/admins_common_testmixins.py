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
                for element in selector.list('.devilry-admin-adminlist-shortname')]

    def __get_names(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-admin-adminlist-name')]

    def test_remove_not_shown_for_requesting_user(self):
        testuser = UserBuilder2().user
        builder = self.builderclass.make()\
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_remove_shown_for_requesting_user_if_superuser(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make()\
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertTrue(selector.exists(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_remove_shown_other_than_requesting_user(self):
        testuser = UserBuilder2().user
        builder = self.builderclass.make()\
            .add_admins(testuser, UserBuilder2(shortname='other').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(1, selector.count(
            '#objecttableview-table tbody .devilry-admin-adminlist-remove-button'))

    def test_ordering(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make()\
            .add_admins(UserBuilder2(shortname='userb').user,
                        UserBuilder2(shortname='usera').user,
                        UserBuilder2(shortname='userc').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['usera', 'userb', 'userc'], self.__get_shortnames(selector))

    def test_render_user_with_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make()\
            .add_admins(UserBuilder2(shortname='test', fullname='Test User').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['Test User(test)'], self.__get_names(selector))

    def test_render_user_without_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = self.builderclass.make()\
            .add_admins(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['test'], self.__get_names(selector))

    def test_render_only_users_from_current_basenode(self):
        testuser = UserBuilder2(is_superuser=True).user
        self.builderclass.make()\
            .add_admins(UserBuilder2(shortname='otherbasenodeuser').user)
        builder = self.builderclass.make()\
            .add_admins(UserBuilder2(shortname='expecteduser').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['expecteduser'], self.__get_names(selector))
