from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field

from devilry.devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormBase
from devilry.devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorFormView
from devilry.devilry_gradingsystem.views.feedbackbulkeditorbase import FeedbackBulkEditorFormBase
from devilry.devilry_gradingsystem.views.feedbackbulkeditorbase import FeedbackBulkEditorFormView


class PointsFeedbackEditorFormMixin(object):
    """
    Common mixin for bulk and single editing forms. They both render the same
    form, but they inherit from different superclasses.
    """
    def setup_form(self):
        self.fields['points'] = forms.IntegerField(
            required=True,
            min_value = 0,
            max_value = self.assignment.max_points,
            help_text = _('Number between 0 and {max_points}.').format(
                max_points=self.assignment.max_points),
            label=_('Points'))
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('points')
        )
        self.add_common_layout_elements()


class PointsFeedbackEditorForm(FeedbackEditorFormBase, PointsFeedbackEditorFormMixin):
    def __init__(self, *args, **kwargs):
        super(PointsFeedbackEditorForm, self).__init__(*args, **kwargs)
        self.setup_form()        


class PointsFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = PointsFeedbackEditorForm

    def get_initial_from_last_draft(self):
        initial = super(PointsFeedbackEditorView, self).get_initial_from_last_draft()
        initial['points'] = self.last_draft.points
        return initial

    def get_points_from_form(self, form):
        return form.cleaned_data['points']



class PointsFeedbackBulkEditorForm(FeedbackBulkEditorFormBase, PointsFeedbackEditorFormMixin):
    def __init__(self, *args, **kwargs):
        super(PointsFeedbackBulkEditorForm, self).__init__(*args, **kwargs)
        self.setup_form()

class PointsFeedbackBulkEditorView(FeedbackBulkEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackbulkeditor.django.html'
    form_class = PointsFeedbackBulkEditorForm

    def get_initial_from_draft(self, draft):
        initial = super(PointsFeedbackBulkEditorView, self).get_initial_from_draft(draft)
        initial['points'] = draft.points
        return initial

    def get_default_points_value(self):
        return ''

    def get_points_from_form(self, form):
        return form.cleaned_data['points']

