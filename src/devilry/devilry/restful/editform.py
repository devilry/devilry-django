from django.db.models import DateTimeField
from django import forms

from fields import RawWithFallbackField


def _create_editform(cls):
    """
    Generates an inner class named EditForm from ``Meta.resultfields``::

        class EditForm(django.forms.ModelForm):
            class Meta:
                model = cls._meta.simplified._meta.model
                fields = fields_deduced_from_resultfields
    """
    extra_classattributes = {}
    model = cls._meta.simplified._meta.model
    for fieldname in cls._meta.simplified._meta.editablefields:
        field = model._meta.get_field_by_name(fieldname)[0]
        if isinstance(field, DateTimeField):
            input_formats = input_formats=['%Y-%m-%dT%H:%M:%S',
                                           '%Y-%m-%d %H:%M:%S'] # TODO: More datetime input formats
            required = not field.blank
            extra_classattributes[fieldname] = forms.DateTimeField(input_formats=input_formats,
                                                                   required=required,
                                                                   label=field.verbose_name,
                                                                   help_text=field.help_text,
                                                                   initial=field.default)

    alleditablefields = list(cls._meta.simplified._meta.editablefields)
    for fakefieldname in cls._meta.simplified._meta.fake_editablefields:
        alleditablefields.append(fakefieldname)
        formfield = cls._meta.fake_editablefields_formfields.get(fakefieldname,
                                                                 RawWithFallbackField())
        extra_classattributes[fakefieldname] = formfield


    class Meta:
        model = cls._meta.simplified._meta.model
        fields = alleditablefields
    extra_classattributes['Meta'] = Meta

    EditForm = type('EditForm', (forms.ModelForm,), extra_classattributes)
    cls.EditForm = EditForm
