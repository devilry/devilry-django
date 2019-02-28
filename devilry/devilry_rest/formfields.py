"""
Form fields that are useful only for REST APIs.
"""
from django import forms
from django.core.exceptions import ValidationError


class ListOfDictField(forms.Field):

    def validate_to_python(self, value):
        """
        Validate and clean data.
        """
        super(ListOfDictField, self).validate(value)
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Must be a list or tuple, got {0}'.format(type(value).__name__))
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


class DictField(forms.Field):

    def validate_to_python(self, value):
        """
        Validate and clean data.
        """
        super(DictField, self).validate(value)
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValidationError('Must be a dict, got {0}'.format(type(value).__name__))
        form = self.Form(value)
        if form.is_valid():
            return form.cleaned_data
        else:
            errors = form.errors.as_text()
            raise ValidationError(errors)

    def clean(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises ValidationError for any errors.
        """
        value = self.validate_to_python(value)
        self.run_validators(value)
        return value


class ListOfTypedField(forms.Field):
    def __init__(self, *args, **kwargs):
        """
        A field similar to TypedChoiceField that takes a list of items and a
        ``coerce`` function that is applied to all items in the given list.
        """
        self.coerce = kwargs.pop('coerce', id)
        super(ListOfTypedField, self).__init__(*args, **kwargs)

    def validate_to_python(self, valuelist):
        """
        Validate and clean data.
        """
        super(ListOfTypedField, self).validate(valuelist)
        if valuelist is None:
            return []
        if not isinstance(valuelist, (list, tuple)):
            raise ValidationError('Must be a list or tuple, got {0}'.format(type(valuelist).__name__))
        cleaned = []
        for index, value in enumerate(valuelist):
            try:
                cleaned_value = self.coerce(value)
            except ValueError as e:
                raise ValidationError('Item {0}: {1}', index, e)
            else:
                cleaned.append(cleaned_value)
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
