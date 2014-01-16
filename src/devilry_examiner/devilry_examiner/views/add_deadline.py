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
from crispy_forms.layout import HTML
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Assignment
from devilry_examiner.forms import GroupIdsForm
from .crispylayout import DefaultSubmit
from .bulkviewbase import BulkViewBase



class DevilryDatetimeFormField(forms.DateTimeField):
    def __init__(self, **kwargs):
        input_formats = kwargs.pop('input_formats', ['%Y-%m-%d %H:%M'])
        error_messages = kwargs.pop('error_messages', {
            'invalid': _('Enter a valid date/time. Example "2014-12-24 18:00" to specify Dec 24 2014 6pm.')
        })
        kwargs.update({
            'input_formats': input_formats,
            'error_messages': error_messages
        })
        super(DevilryDatetimeFormField, self).__init__(**kwargs)



class AddDeadlineForm(GroupIdsForm):
    deadline = DevilryDatetimeFormField(
        label=_('Deadline'),
        help_text=_('Format YYYY-MM-DD hh:mm'),
    )
    text = forms.CharField(
        label=_('Text'),
        help_text=_('Why are you adding this deadline? Make this informative, and remember that this information may be important for course administrators if they need to move the deadline.'),
        widget=forms.Textarea(attrs={'rows': 7}),
        required=False)
    no_text = forms.BooleanField(
        label=_('I do not want to provide a deadline text.'),
        help_text=_('You should normally tell your students why they get a new deadline. If some rare cases this makes no sense, so you can select this option to avoid specifying a text.'),
        required=False, initial=False)

    def clean(self):
        cleaned_data = super(AddDeadlineForm, self).clean()
        deadline = cleaned_data.get('deadline')
        if deadline and hasattr(self, 'cleaned_groups'):
            if self.cleaned_groups.filter(last_deadline__deadline__gt=deadline).exists():
                raise forms.ValidationError('The last deadline of one or more of the selected groups is after the selected deadline.')

        text = cleaned_data.get('text', None)
        no_text = cleaned_data.get('no_text', False)
        if not text and not no_text:
            error_message = _('You must specify a deadline text, or select that you do not want to specify any text.')
            self._errors["text"] = self.error_class([error_message])
            self._errors["no_text"] = self.error_class([error_message])
            if 'text' in cleaned_data:
                del cleaned_data['text']
            if 'no_text' in cleaned_data:
                del cleaned_data['no_text']

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(AddDeadlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('deadline', placeholder='YYYY-MM-DD hh:mm'),
            'text',
            'no_text',
            'group_ids',
            HTML('<hr>'),
            ButtonHolder(
                Submit('submit_primary', _('Add deadline'), css_class='pull-right'),
                DefaultSubmit('submit_cancel', _('Cancel')),
            )
        )


class AddDeadlineView(BulkViewBase):
    template_name = "devilry_examiner/add_deadline.django.html"
    form_class = AddDeadlineForm

    def form_valid(self, form):
        Deadline.objects.smart_create(
            form.cleaned_groups,
            deadline_datetime=form.cleaned_data['deadline'],
            text=form.cleaned_data['text'])
        return super(AddDeadlineView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddDeadlineView, self).get_context_data(**kwargs)
        return context