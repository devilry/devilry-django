from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormBase
from devilry.devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormView
from devilry.devilry_gradingsystem.views.feedbackbulkeditorbase import FeedbackBulkEditorFormBase
from devilry.devilry_gradingsystem.views.feedbackbulkeditorbase import FeedbackBulkEditorFormView
from devilry.devilry_gradingsystem.models import FeedbackDraft


class ApprovedFeedbackEditorForm(FeedbackEditorFormBase):
    points = forms.BooleanField(
        label=_('Passed?'),
        help_text=_('Check to provide a passing grade.'),
        initial=True,
        required=False)

    def __init__(self, *args, **kwargs):
        super(ApprovedFeedbackEditorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('points')
        )
        self.add_common_layout_elements()


class ApprovedFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_approved/feedbackeditor.django.html'
    form_class = ApprovedFeedbackEditorForm

    def get_initial_from_last_draft(self):
        initial = super(ApprovedFeedbackEditorView, self).get_initial_from_last_draft()
        initial['points'] = bool(self.last_draft.points)
        return initial

    def get_points_from_form(self, form):
        if form.cleaned_data['points']:
            return 1
        return 0


class ApprovedFeedbackBulkEditorForm(FeedbackBulkEditorFormBase):
    points = forms.BooleanField(
        label=_('Passed?'),
        help_text=_('Check to provide a passing grade.'),
        required=False)

    def __init__(self, *args, **kwargs):
        super(ApprovedFeedbackBulkEditorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('points')
        )
        self.add_common_layout_elements()


class ApprovedFeedbackBulkEditorView(FeedbackBulkEditorFormView):
    template_name = 'devilry_gradingsystemplugin_approved/feedbackbulkeditor.django.html'
    form_class = ApprovedFeedbackBulkEditorForm

    def get_initial_from_draft(self, draft):
        initial = super(ApprovedFeedbackBulkEditorView, self).get_initial_from_draft(draft)
        initial['points'] = draft.points
        return initial

    def get_default_points_value(self):
        return False

    def get_points_from_form(self, form):
        if form.cleaned_data['points']:
            return 1
        return 0
