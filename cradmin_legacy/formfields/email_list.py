import re

from django import forms
from django.core import validators
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy


class EmailListField(forms.Field):
    """
    A form field that parses and validates a list of email addresses.

    The input can be a list, tuple or string. If it is a string,
    we split the email addresses by whitespace or comma.
    """

    default_error_messages = {
        "invalid": gettext_lazy("Type email-addresses separated by newlines, whitespace or comma.")
    }
    default_help_text = gettext_lazy("Type email-addresses separated by newlines, whitespace or comma.")
    widget = forms.Textarea
    stringsplit_regex = re.compile(r"(?:\s*,\s*)|\s+")
    email_validator = EmailValidator()

    def __init__(self, *args, **kwargs):
        """
        Works just like any other form field.

        Parameters are just like for any other form field, with the
        addition of the ``extra_help_text`` parameter. The ``extra_help_text``
        parameter can be used to append help text to the default help text.
        """
        if "help_text" not in kwargs:
            kwargs["help_text"] = self.default_help_text
        extra_help_text = kwargs.pop("extra_help_text", None)
        if extra_help_text:
            kwargs["help_text"] = "{} {}".format(kwargs["help_text"], extra_help_text)
        super().__init__(*args, **kwargs)

    def string_to_list(self, value):
        value = value.strip()
        if value.strip():
            return self.stringsplit_regex.split(value)
        else:
            return []

    def to_python_list(self, value):
        if value in validators.EMPTY_VALUES:
            return []
        elif isinstance(value, list):
            return value
        elif isinstance(value, tuple):
            return list(value)
        elif isinstance(value, str):
            return self.string_to_list(value)
        else:
            raise TypeError(f"Invalid type for EmailListField: {type(value)}")

    def validate_list_of_emails(self, list_of_emails):
        for email in list_of_emails:
            try:
                self.email_validator(email)
            except forms.ValidationError:
                errormessage = gettext_lazy("Invalid email address: %(email)s") % {"email": email}
                raise forms.ValidationError(errormessage)

    def to_python(self, value):
        list_of_emails = self.to_python_list(value)
        self.validate_list_of_emails(list_of_emails)
        return list_of_emails
