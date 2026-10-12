from django.test import TestCase
from cradmin_legacy.apps.cradmin_register_account.forms.email import EmailUserCreateAccountForm
from cradmin_legacy.apps.cradmin_register_account.tests.cradmin_register_account_testapp.models import EmailUser


class EmailUserCreateAccountFormStaticUserModel(EmailUserCreateAccountForm):
    class Meta(EmailUserCreateAccountForm.Meta):
        model = EmailUser


class TestEmailUserCreateAccountForm(TestCase):
    def test_is_valid(self):
        form = EmailUserCreateAccountFormStaticUserModel(
            {"password1": "test", "password2": "test", "email": "test@example.com"}
        )
        self.assertTrue(form.is_valid())

    def test_save(self):
        form = EmailUserCreateAccountFormStaticUserModel(
            {"password1": "test", "password2": "test", "email": "test@example.com"}
        )
        form.is_valid()
        self.assertEqual(EmailUser.objects.count(), 0)
        form.save()
        self.assertEqual(EmailUser.objects.count(), 1)
        created_user = EmailUser.objects.first()
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.has_usable_password())
        self.assertTrue(created_user.check_password("test"))

    def test_passwords_do_not_match(self):
        form = EmailUserCreateAccountFormStaticUserModel(
            {"password1": "test1", "password2": "test2", "email": "unused@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ["The passwords do not match."])

    def test_email_is_not_unique(self):
        EmailUser.objects.create(email="test@example.com")
        form = EmailUserCreateAccountFormStaticUserModel(
            {"password1": "unused", "password2": "unused", "email": "test@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"email": ["Email user with this Email already exists."]})
