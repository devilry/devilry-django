from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import Hidden
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Assignment
from devilry_examiner.forms import GroupIdsForm
from .crispylayout import DefaultSubmit
from .bulkviewbase import BulkViewBase


class AddDeadlineForm(GroupIdsForm):
    deadline = forms.DateTimeField()
    text = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(AddDeadlineForm, self).clean()
        deadline = cleaned_data.get('deadline')
        if deadline and hasattr(self, 'cleaned_groups'):
            if self.cleaned_groups.filter(last_deadline__deadline__gt=deadline).exists():
                raise forms.ValidationError('The last deadline of one or more of the selected groups is after the selected deadline.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(AddDeadlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'deadline',
            'text',
            'group_ids',
            ButtonHolder(
                DefaultSubmit('submit_go_back', _('Back')),
                Submit('submit_add_deadline', _('Add deadline'))
            )
        )


class AddDeadlineView(BulkViewBase):
    template_name = "devilry_examiner/add_deadline.django.html"
    form_class = AddDeadlineForm

    def form_valid(self, form):
        print
        print 'Create deadline on:'
        for group in form.cleaned_groups:
            print group
        print
        return super(AddDeadlineView, self).form_valid()


    def get_context_data(self, **kwargs):
        context = super(AddDeadlineView, self).get_context_data(**kwargs)
        print context['form']
        print context['group_ids_form']
        return context