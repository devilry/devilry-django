import unittest
from django import test

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker
from dateutil.parser import parse

from devilry.devilry_import_v2database.scripts import user_add_missing_data_from_json


@unittest.skip('Not relevant anymore, keep for history.')
class TestScript(test.TestCase):
    def __make_v2_user_json_data(self, pk, username, last_login):
        return {
            "pk": pk,
            "model": "auth.user",
            "fields": {
                "username": username,
                "last_login": last_login
            }
        }

    def __make_v3_user(self, id, shortname, last_login=None):
        return baker.make(settings.AUTH_USER_MODEL, id=id, shortname=shortname, last_login=last_login)

    def test_does_not_update_user_without_v2_id(self):
        v2_user_data = [
            self.__make_v2_user_json_data(pk=1, username='testuser', last_login='2014-01-29T20:38:38.134')
        ]
        v3_user = self.__make_v3_user(id=2, shortname='testuser')
        user_add_missing_data_from_json.add_missing_data_from_json_data(v2_user_data=v2_user_data)
        v3_user.refresh_from_db()
        self.assertIsNone(v3_user.last_login)

    def test_does_not_update_user_with_v2_id_but_last_login_set(self):
        v2_user_data = [
            self.__make_v2_user_json_data(pk=1, username='testuser', last_login='2014-01-29T20:38:38.134')
        ]
        v3_user_last_login = timezone.now()
        v3_user = self.__make_v3_user(id=1, shortname='testuser', last_login=v3_user_last_login)
        user_add_missing_data_from_json.add_missing_data_from_json_data(v2_user_data=v2_user_data)
        v3_user.refresh_from_db()
        self.assertEqual(v3_user.last_login, v3_user_last_login)

    def test_updates_user_with_v2_id_mismatching_usernames(self):
        v2_user_data = [
            self.__make_v2_user_json_data(pk=1, username='v2testuser', last_login='2014-01-29T20:38:38.134')
        ]
        v3_user = self.__make_v3_user(id=1, shortname='v3testuser')
        user_add_missing_data_from_json.add_missing_data_from_json_data(v2_user_data=v2_user_data)
        v3_user.refresh_from_db()
        self.assertIsNone(v3_user.last_login)

    def test_updates_user_with_v2_id_and_last_login_none(self):
        v2_user_data = [
            self.__make_v2_user_json_data(pk=1, username='testuser', last_login='2014-01-29T20:38:38.134')
        ]
        v3_user = self.__make_v3_user(id=1, shortname='testuser')
        user_add_missing_data_from_json.add_missing_data_from_json_data(v2_user_data=v2_user_data)
        v3_user.refresh_from_db()
        self.assertEqual(v3_user.last_login, timezone.make_aware(parse('2014-01-29T20:38:38.134')))

    def test_updates_multiple_users_with_v2_id_and_last_login_none(self):
        v2_user1_data = self.__make_v2_user_json_data(pk=1, username='testuser1', last_login='2014-01-29T20:38:38.134')
        v2_user2_data = self.__make_v2_user_json_data(pk=2, username='testuser2', last_login='2015-01-29T20:38:38.134')
        v2_user3_data = self.__make_v2_user_json_data(pk=3, username='testuser3', last_login='2016-01-29T20:38:38.134')
        v2_user_data = [v2_user1_data, v2_user2_data, v2_user3_data]

        v3_user1 = self.__make_v3_user(id=1, shortname='testuser1')
        v3_user2 = self.__make_v3_user(id=2, shortname='testuser2')
        v3_user3 = self.__make_v3_user(id=3, shortname='testuser3')

        user_add_missing_data_from_json.add_missing_data_from_json_data(v2_user_data=v2_user_data)
        self.assertEqual(
            get_user_model().objects.get(id=v3_user1.id).last_login,
            timezone.make_aware(parse(v2_user1_data['fields']['last_login'])))
        self.assertEqual(
            get_user_model().objects.get(id=v3_user2.id).last_login,
            timezone.make_aware(parse(v2_user2_data['fields']['last_login'])))
        self.assertEqual(
            get_user_model().objects.get(id=v3_user3.id).last_login,
            timezone.make_aware(parse(v2_user3_data['fields']['last_login'])))
