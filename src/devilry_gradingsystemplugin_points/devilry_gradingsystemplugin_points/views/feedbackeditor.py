from django.views.generic import FormView
from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorMixin



class PointsFeedbackEditorForm(forms.Form):
    points = forms.IntegerField(
        label=_('Points'))
    feedbacktext_raw = forms.CharField()
    feedbacktext_html = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'points',
            'feedbacktext_raw',
            'feedbacktext_html',
            ButtonHolder(
                Submit('submit', 'Submit')
            )
        )
        super(PointsFeedbackEditorForm, self).__init__(*args, **kwargs)



class PointsFeedbackEditorView(FeedbackEditorMixin, FormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = PointsFeedbackEditorForm

    def get(self, request, deliveryid):
        self.object = self.get_object()
        return super(PointsFeedbackEditorView, self).get(request, deliveryid)

    # def form_valid(self, form):
    #     return super(PointsFeedbackEditorView, self).form_valid(form)