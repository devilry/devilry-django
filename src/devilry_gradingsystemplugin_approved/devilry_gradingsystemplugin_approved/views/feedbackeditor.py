from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field

from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormBase
from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormView
from devilry_gradingsystem.models import FeedbackDraft


class ApprovedFeedbackEditorForm(FeedbackEditorFormBase):
    points = forms.IntegerField(
        label=_('Points'))

    def __init__(self, *args, **kwargs):
        super(PointsFeedbackEditorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('points')
        )
        self.add_common_layout_elements()


class ApprovedFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = ApprovedFeedbackEditorForm

    def get_initial_from_last_draft(self):
        initial = super(PointsFeedbackEditorView, self).get_initial_from_last_draft()
        initial['points'] = self.last_draft.points
        return initial

    def get_points_from_form(self, form):
        return form.cleaned_data['points']
