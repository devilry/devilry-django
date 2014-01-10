from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Submit
from crispy_forms.layout import Button
from crispy_forms.layout import Field

from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorMixin
from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormBase
from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormView
from devilry_gradingsystem.models import FeedbackDraft


class DefaultSubmitButton(Submit):
    field_classes = 'btn btn-default'


class PointsFeedbackEditorForm(FeedbackEditorFormBase):
    points = forms.IntegerField(
        label=_('Points'))

    def __init__(self, *args, **kwargs):
        super(PointsFeedbackEditorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('points'),
            'feedbacktext',
            ButtonHolder(
                DefaultSubmitButton('save_draft', _('Save draft')),
                Submit('publish', _('Publish'))
            )
        )


class PointsFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = PointsFeedbackEditorForm

    def get_success_url(self):
        publish = 'publish' in self.request.POST
        if publish:
            return super(PointsFeedbackEditorView, self).get_success_url()
        else:
            return self.request.path

    def form_valid(self, form):
        publish = 'publish' in self.request.POST
        #save_draft = 'save_draft' in self.request.POST
        self.create_feedbackdraft(
           points=form.cleaned_data['points'],
           feedbacktext_raw=form.cleaned_data['feedbacktext'],
           feedbacktext_html=form.cleaned_data['feedbacktext'],
           publish=publish
        )
        return super(PointsFeedbackEditorView, self).form_valid(form)