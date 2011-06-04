from django import forms
import fields

class GetFormBase(forms.Form):
    format = fields.FormatField()
    query = forms.CharField(required=False)
    limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
    start = fields.PositiveIntegerWithFallbackField()
    #page = fields.PositiveIntegerWithFallbackField()
