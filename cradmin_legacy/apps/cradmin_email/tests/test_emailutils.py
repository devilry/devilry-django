from django.core import mail
from django.test import TestCase
from cradmin_legacy.apps.cradmin_email import emailutils


class TestConvertHtmlToPlaintext(TestCase):
    def test_single_paragraph(self):
        self.assertEqual(emailutils.convert_html_to_plaintext("<p>Hello</p>").strip(), "Hello")

    def test_multiple_paragraphs(self):
        self.assertEqual(emailutils.convert_html_to_plaintext("<p>Hello</p><p>World</p>").strip(), "Hello\n\nWorld")

    def test_bold(self):
        self.assertEqual(emailutils.convert_html_to_plaintext("<strong>Hello</strong>").strip(), "**Hello**")

    def test_italic(self):
        self.assertEqual(emailutils.convert_html_to_plaintext("<em>Hello</em>").strip(), "_Hello_")

    def test_link(self):
        self.assertEqual(
            emailutils.convert_html_to_plaintext('<a href="http://example.com">Example</a>').strip(),
            "[Example](http://example.com)",
        )

    def test_link_with_classes(self):
        self.assertEqual(
            emailutils.convert_html_to_plaintext('<a href="http://example.com" class="btn">Example</a>').strip(),
            "[Example](http://example.com)",
        )


class TestAbstractEmail(TestCase):
    def test_subject(self):
        class MyEmail(emailutils.AbstractEmail):
            subject_template = "cradmin_email_testapp/abstractemail/subject.django.txt"
            html_message_template = "cradmin_email_testapp/abstractemail/html_message.django.html"

        MyEmail(recipient="test@example.com", extra_context_data={"name": "Test"}).send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hello, Test")

    def test_subject_prefix(self):
        class MyEmail(emailutils.AbstractEmail):
            subject_template = "cradmin_email_testapp/abstractemail/subject.django.txt"
            html_message_template = "cradmin_email_testapp/abstractemail/html_message.django.html"

        with self.settings(CRADMIN_LEGACY_EMAIL_SUBJECT_PREFIX="[Testbrand] "):
            MyEmail(recipient="test@example.com", extra_context_data={"name": "Test"}).send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[Testbrand] Hello, Test")

    def test_html_message(self):
        class MyEmail(emailutils.AbstractEmail):
            subject_template = "cradmin_email_testapp/abstractemail/subject.django.txt"
            html_message_template = "cradmin_email_testapp/abstractemail/html_message.django.html"

        MyEmail(recipient="test@example.com", extra_context_data={"name": "Test"}).send()
        html_altenative = mail.outbox[0].alternatives[0]
        self.assertEqual(html_altenative[1], "text/html")
        self.assertEqual(html_altenative[0].strip(), "<p>Hello</p><p>World</p><p>Test</p>")

    def test_plaintext_message_from_html_message(self):
        class MyEmail(emailutils.AbstractEmail):
            subject_template = "cradmin_email_testapp/abstractemail/subject.django.txt"
            html_message_template = "cradmin_email_testapp/abstractemail/html_message.django.html"

        MyEmail(recipient="test@example.com", extra_context_data={"name": "Test"}).send()
        self.assertEqual(mail.outbox[0].body.strip(), "Hello\n\nWorld\n\nTest")

    def test_plaintext_message_from_template(self):
        class MyEmail(emailutils.AbstractEmail):
            subject_template = "cradmin_email_testapp/abstractemail/subject.django.txt"
            html_message_template = "cradmin_email_testapp/abstractemail/html_message.django.html"
            plaintext_message_template = "cradmin_email_testapp/abstractemail/plaintext_message.django.txt"

        MyEmail(recipient="test@example.com", extra_context_data={"name": "Test"}).send()
        self.assertEqual(mail.outbox[0].body.strip(), "Hello PlainText World Test")
