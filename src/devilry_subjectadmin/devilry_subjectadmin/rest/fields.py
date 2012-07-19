from django import forms
from django.core.exceptions import ValidationError


class ListOfDictField(forms.Field):

    def validate_to_python(self, value):
        """
        Validate and clean data.
        """
        super(ListOfDictField, self).validate(value)
        if value == None:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Must be a list or tuple')
        cleaned = []
        for index, dct in enumerate(value):
            if not isinstance(dct, dict):
                raise ValidationError('Item {0}: Must be a list of dicts, got {1}'.format(index, type(value)))
            form = self.Form(dct)
            if form.is_valid():
                cleaned.append(form.cleaned_data)
            else:
                errors = form.errors.as_text()
                raise ValidationError('Item {0}: Invalid format:\n{1}'.format(index, errors))
        return cleaned

    def clean(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises ValidationError for any errors.
        """
        value = self.validate_to_python(value)
        self.run_validators(value)
        return value
