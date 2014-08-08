from django import forms

import fields


class ReadForm(forms.Form):
    """ The form used to validate ``read()`` input. """
    result_fieldgroups = fields.JsonListWithFallbackField()
