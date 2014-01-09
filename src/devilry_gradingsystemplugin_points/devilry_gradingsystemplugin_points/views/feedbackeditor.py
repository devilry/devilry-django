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
                Button('save-draft', _('Save draft'), css_class="btn-default", type='submit'),
                Submit('publish', _('Publish'))
            )
        )


class PointsFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = PointsFeedbackEditorForm


    # def form_valid(self, form):
    #     return super(PointsFeedbackEditorView, self).form_valid(form)