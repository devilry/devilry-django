from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import HTML
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Deadline
from .crispylayout import DefaultSubmit
from .bulkviewbase import BulkViewBase
from .bulkviewbase import OptionsForm


class DevilryDatetimeFormField(forms.DateTimeField):
    def __init__(self, **kwargs):
        input_formats = kwargs.pop('input_formats', ['%Y-%m-%d %H:%M'])
        error_messages = kwargs.pop('error_messages', {
            'invalid': _('Enter a valid date/time. Example "2014-12-24 18:00" to specify Dec 24 2014 6pm.')
        })
        widget = kwargs.pop('widget', forms.DateTimeInput(format='%Y-%m-%d %H:%M'))
        kwargs.update({
            'input_formats': input_formats,
            'error_messages': error_messages,
            'widget': widget
        })
        super(DevilryDatetimeFormField, self).__init__(**kwargs)


class AddDeadlineOptionsForm(OptionsForm):
    give_another_chance = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput())


class AddDeadlineForm(AddDeadlineOptionsForm):
    deadline = DevilryDatetimeFormField(
        label=_('Deadline'),
        help_text=_('Format: "YYYY-MM-DD hh:mm".'),
    )
    text = forms.CharField(
        label=_('About this deadline'),
        help_text=_('Why are you adding this deadline? Make this informative, and remember that this information may be important for course administrators if they need to move the deadline.'),
        widget=forms.Textarea(attrs={'rows': 7}),
        required=False)
    no_text = forms.BooleanField(
        label=_('I do not want to provide an "About this deadline" message.'),
        help_text=_('You should normally tell your students why they get a new deadline. In some rare cases this makes no sense, so you can select this option to avoid specifying a text.'),
        required=False, initial=False)
    why_created = forms.ChoiceField(
        required=False,
        widget=forms.HiddenInput,
        choices=(
            (None, 'unknown'),
            ('examiner-gave-another-chance', 'Another chance.'))
        )

    def clean(self):
        cleaned_data = super(AddDeadlineForm, self).clean()
        deadline = cleaned_data.get('deadline')
        if deadline and hasattr(self, 'cleaned_groups'):
            if self.cleaned_groups.filter(last_deadline__deadline__gt=deadline).exists():
                raise forms.ValidationError('The last deadline of one or more of the selected groups is after the selected deadline.')

        text = cleaned_data.get('text', None)
        no_text = cleaned_data.get('no_text', False)
        if not text and not no_text:
            error_message = _('You must specify an "About this deadline" message, or select that you do not want to specify a message.')
            self._errors["text"] = self.error_class([error_message])
            self._errors["no_text"] = self.error_class([error_message])
            if 'text' in cleaned_data:
                del cleaned_data['text']
            if 'no_text' in cleaned_data:
                del cleaned_data['no_text']
        if text and no_text:
            error_message = _('If you do not want to provide an "About this deadline" message, you have to clear the text field.')
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
            'success_url',
            'cancel_url',
            'why_created',
            HTML('<hr>'),
            ButtonHolder(
                Submit('add_deadline_form', _('Add deadline'), css_class='pull-right'),
                DefaultSubmit('submit_cancel', _('Cancel')),
            )
        )


class AddDeadlineView(BulkViewBase):
    """
    A bulk view for adding deadlines to one or more groups.

    Provides a few tools useful when adding deadline for a single
    group (I.E. after failing a single group):

    - Can specify ``success_url`` and ``cancel_url`` in the querystring.
    - Can specify ``give_another_chance`` in the querystring, to provide a default
      message that examiners can use, edit or clear.
    """
    template_name = "devilry_examiner/add_deadline.django.html"
    optionsform_class = AddDeadlineOptionsForm
    primaryform_classes = {
        'add_deadline_form': AddDeadlineForm
    }

    def submitted_primaryform_valid(self, form, context_data):
        Deadline.objects.smart_create(
            form.cleaned_groups,
            deadline_datetime=form.cleaned_data['deadline'],
            text=form.cleaned_data['text'],
            added_by=self.request.user,
            why_created=form.cleaned_data['why_created'])
        return super(AddDeadlineView, self).submitted_primaryform_valid(form, context_data)

    def get_primaryform_initial_data(self, formclass):
        initial = super(AddDeadlineView, self).get_primaryform_initial_data(formclass)
        if self.optionsdict['give_another_chance']:
            initial.update({
                'text': _('I have given you a new chance to pass this assignment. Read your last feedback for information about why you did not pass, and why you have been given another chance.'),
                'why_created': 'examiner-gave-another-chance'
            })
        return initial
