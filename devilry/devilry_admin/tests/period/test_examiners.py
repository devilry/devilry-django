from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_admin.views.period import examiners
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder2


class TestExaminerListView(TestCase):
    def __mock_get_request(self, role, user):
        request = RequestFactory().get('/')
        request.user = user
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = examiners.ExaminerListView.as_view()(request)
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

    def test_remove_not_shown_for_requesting_user(self):
        testuser = UserBuilder2().user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists(
            '#objecttableview-table tbody .devilry-relatedexaminerlist-remove-button'))

    def test_remove_shown_for_requesting_user_if_superuser(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(testuser)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertTrue(selector.exists(
            '#objecttableview-table tbody .devilry-relatedexaminerlist-remove-button'))

    def test_remove_shown_other_than_requesting_user(self):
        testuser = UserBuilder2().user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(testuser, UserBuilder2(shortname='other').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(1, selector.count(
            '#objecttableview-table tbody .devilry-relatedexaminerlist-remove-button'))

    def test_ordering(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='userb').user,
                                  UserBuilder2(shortname='usera').user,
                                  UserBuilder2(shortname='userc').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['usera', 'userb', 'userc'], self.__get_shortnames(selector))

    def test_render_user_with_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test', fullname='Test User').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['Test User(test)'], self.__get_names(selector))

    def test_render_user_without_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['test'], self.__get_names(selector))

    def test_render_email_has_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').add_primary_email('test@example.com').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('.devilry-admin-adminlist-email').alltext_normalized,
                         'Contact at test@example.com')
        self.assertEqual(selector.one('.devilry-admin-adminlist-email')['href'],
                         'mailto:test@example.com')

    def test_render_email_no_primary_email(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='test').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('.devilry-admin-adminlist-email')),

    def test_render_only_users_from_current_basenode(self):
        testuser = UserBuilder2(is_superuser=True).user
        PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='otherbasenodeuser').user)
        builder = PeriodBuilder.make() \
            .add_relatedexaminers(UserBuilder2(shortname='expecteduser').user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(['expecteduser'], self.__get_names(selector))

# class TestRemoveExaminerView(TestCase):
#
#
# class TestExaminerUserSelectView(TestCase):
#
#
# class TestAddExaminerView(TestCase):
