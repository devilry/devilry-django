from django import forms


class BulkForm(forms.Form):
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                       label="Bulktest:")
