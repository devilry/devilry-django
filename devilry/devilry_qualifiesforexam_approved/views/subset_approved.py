from django.utils.translation import ugettext_lazy as _
from devilry.apps.core.models import Assignment
from django import forms
from django_cradmin.viewhelpers.formbase import FormView


class SelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.period = kwargs.pop('period')
        super(SelectForm, self).__init__(*args, **kwargs)
        val = Assignment.objects.filter(parentnode=self.period).values_list('id', 'long_name')
        self.fields['choices'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=val,
            required=True
        )


class SubsetApprovedView(FormView):
    template_name = 'devilry_qualifiesforexam_approved/subset.django.html'
    form_class = SelectForm

    def get_pagetitle(self):
        return _('Select assignments to qualify')

    def get_form_kwargs(self):
        kwargs = super(SubsetApprovedView, self).get_form_kwargs()
        kwargs['period'] = self.request.cradmin_role
        return kwargs

    def get_field_layout(self):
        return [
            'choices',
        ]

    def get_buttons(self):
        return []