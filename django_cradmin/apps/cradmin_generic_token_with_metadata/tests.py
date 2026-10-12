from datetime import datetime, timedelta

import arrow
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    generate_token,
    get_expiration_datetime_for_app,
)
from unittest import mock
from django_cradmin.tests.helpers import create_user


class TestGenericTokenWithMetadata(TestCase):
    def _create_generic_token_with_metadata(
        self, user, created_datetime=None, expiration_datetime=None, app="testapp", **kwargs
    ):
        generic_token_with_metadata = GenericTokenWithMetadata.objects.create(
            created_datetime=(created_datetime or timezone.now()),
            expiration_datetime=(expiration_datetime or (timezone.now() + timedelta(days=2))),
            app=app,
            content_object=user,
            **kwargs,
        )
        return generic_token_with_metadata

    def test_generate_token(self):
        self.assertEqual(len(generate_token()), 73)
        self.assertNotEqual(generate_token(), generate_token())

    def test_generate(self):
        testuser = create_user("testuser")
        unique_user_token = GenericTokenWithMetadata.objects.generate(
            content_object=testuser, app="testapp", expiration_datetime=get_expiration_datetime_for_app("testapp")
        )
        self.assertEqual(unique_user_token.content_object, testuser)
        self.assertEqual(unique_user_token.app, "testapp")
        self.assertEqual(len(unique_user_token.token), 73)

    def test_generate_handle_not_unique(self):
        self._create_generic_token_with_metadata(user=create_user("testuser1"), app="testapp1", token="taken")
        tokens = iter(["taken", "free"])
        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models.generate_token", lambda: next(tokens)
        ):
            unique_user_token = GenericTokenWithMetadata.objects.generate(
                content_object=create_user("testuser2"),
                app="testapp2",
                expiration_datetime=get_expiration_datetime_for_app("testapp"),
            )
        self.assertEqual(unique_user_token.token, "free")

    def test_filter_by_content_object(self):
        testobject1 = create_user("testobject1")
        testobject2 = create_user("testobject2")
        generictoken = GenericTokenWithMetadata.objects.generate(
            content_object=testobject1, app="testapp", expiration_datetime=get_expiration_datetime_for_app("testapp")
        )
        self.assertEqual(GenericTokenWithMetadata.objects.filter_by_content_object(testobject1).get(), generictoken)
        self.assertEqual(GenericTokenWithMetadata.objects.filter_by_content_object(testobject2).count(), 0)

    def test_unsafe_pop(self):
        testuser = create_user("testuser")
        self._create_generic_token_with_metadata(user=testuser, app="testapp1", token="test-token1")
        self._create_generic_token_with_metadata(user=testuser, app="testapp2", token="test-token2")
        self.assertEqual(
            GenericTokenWithMetadata.objects.unsafe_pop(token="test-token1", app="testapp1").content_object, testuser
        )
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 1)
        self.assertEqual(
            GenericTokenWithMetadata.objects.unsafe_pop(token="test-token2", app="testapp2").content_object, testuser
        )
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)

    def test_filter_not_expired(self):
        unexpired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser1"),
            token="test-token1",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )
        self._create_generic_token_with_metadata(
            user=create_user("testuser2"),
            token="test-token2",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            self.assertEqual(GenericTokenWithMetadata.objects.filter_not_expired().count(), 1)
            self.assertEqual(
                GenericTokenWithMetadata.objects.filter_not_expired().first(), unexpired_generic_token_with_metadata
            )

    def test_filter_not_expired_none(self):
        expired_none_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser1"), token="test-token1", expiration_datetime=None
        )
        self._create_generic_token_with_metadata(
            user=create_user("testuser2"),
            token="test-token2",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            self.assertEqual(GenericTokenWithMetadata.objects.filter_not_expired().count(), 1)
            self.assertEqual(
                GenericTokenWithMetadata.objects.filter_not_expired().first(), expired_none_generic_token_with_metadata
            )

    def test_filter_has_expired(self):
        self._create_generic_token_with_metadata(
            user=create_user("testuser1"),
            app="testapp",
            token="test-token1",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )
        self._create_generic_token_with_metadata(
            user=create_user("testuser2"), app="testapp", token="test-token2", expiration_datetime=None
        )
        expired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser3"),
            app="testapp",
            token="test-token3",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            self.assertEqual(GenericTokenWithMetadata.objects.filter_has_expired().count(), 1)
            self.assertEqual(
                GenericTokenWithMetadata.objects.filter_has_expired().first(), expired_generic_token_with_metadata
            )

    def test_pop_not_expired(self):
        testuser = create_user("testuser")
        self._create_generic_token_with_metadata(
            user=testuser,
            token="test-token",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            self.assertEqual(
                GenericTokenWithMetadata.objects.pop(app="testapp", token="test-token").content_object, testuser
            )

    def test_pop_expired(self):
        self._create_generic_token_with_metadata(
            user=create_user("testuser"),
            app="testapp",
            token="test-token",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            with self.assertRaises(GenericTokenWithMetadata.DoesNotExist):
                GenericTokenWithMetadata.objects.pop(app="testapp", token="test-token")

    def test_delete_expired(self):
        unexpired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser1"),
            token="test-token1",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )
        self._create_generic_token_with_metadata(
            user=create_user("testuser2"),
            token="test-token2",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        self.assertEqual(GenericTokenWithMetadata.objects.count(), 2)
        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            GenericTokenWithMetadata.objects.delete_expired()
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 1)
        self.assertEqual(GenericTokenWithMetadata.objects.first(), unexpired_generic_token_with_metadata)

    def test_delete_expired_management_command(self):
        unexpired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser1"),
            token="test-token1",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )
        self._create_generic_token_with_metadata(
            user=create_user("testuser2"),
            token="test-token2",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        self.assertEqual(GenericTokenWithMetadata.objects.count(), 2)
        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            call_command("cradmin_generic_token_with_metadata_delete_expired")
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 1)
        self.assertEqual(GenericTokenWithMetadata.objects.first(), unexpired_generic_token_with_metadata)

    def test_is_expired(self):
        unexpired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser1"),
            token="test-token1",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 14, 30), settings.TIME_ZONE).datetime,
        )
        expired_generic_token_with_metadata = self._create_generic_token_with_metadata(
            user=create_user("testuser2"),
            token="test-token2",
            expiration_datetime=arrow.get(datetime(2015, 1, 1, 13, 30), settings.TIME_ZONE).datetime,
        )

        with mock.patch(
            "django_cradmin.apps.cradmin_generic_token_with_metadata.models._get_current_datetime",
            lambda: arrow.get(datetime(2015, 1, 1, 14), settings.TIME_ZONE).datetime,
        ):
            self.assertFalse(unexpired_generic_token_with_metadata.is_expired())
            self.assertTrue(expired_generic_token_with_metadata.is_expired())

    def test_is_expired_expiration_datetime_none(self):
        tokenobject = self._create_generic_token_with_metadata(
            user=create_user("testuser2"), token="test-token2", expiration_datetime=None
        )
        self.assertFalse(tokenobject.is_expired())
