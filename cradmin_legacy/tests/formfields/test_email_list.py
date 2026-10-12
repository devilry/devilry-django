from django.core.exceptions import ValidationError
from django.test import TestCase
from cradmin_legacy.formfields.email_list import EmailListField


class TestEmailListField(TestCase):
    def test_to_python_none(self):
        self.assertEqual(EmailListField().to_python(None), [])

    def test_to_python_empty_list(self):
        self.assertEqual(EmailListField().to_python([]), [])

    def test_to_python_empty_tuple(self):
        self.assertEqual(EmailListField().to_python(()), [])

    def test_to_python_list(self):
        self.assertEqual(
            EmailListField().to_python(["a@example.com", "b@example.com"]), ["a@example.com", "b@example.com"]
        )

    def test_to_python_tuple(self):
        self.assertEqual(
            EmailListField().to_python(("a@example.com", "b@example.com")), ["a@example.com", "b@example.com"]
        )

    def test_to_python_string(self):
        self.assertEqual(EmailListField().to_python("a@example.com b@example.com"), ["a@example.com", "b@example.com"])

    def test_to_python_empty_string(self):
        self.assertEqual(EmailListField().to_python(""), [])

    def test_to_python_string_with_spaces_only(self):
        self.assertEqual(EmailListField().to_python("     "), [])

    def test_to_python_string_with_spaces_at_beginning(self):
        self.assertEqual(EmailListField().to_python("     x@example.com"), ["x@example.com"])

    def test_to_python_string_with_spaces_at_end(self):
        self.assertEqual(EmailListField().to_python("x@example.com    "), ["x@example.com"])

    def test_to_python_invalid_email(self):
        with self.assertRaisesMessage(ValidationError, "Invalid email address: b"):
            EmailListField().to_python("a@example.com b c")
