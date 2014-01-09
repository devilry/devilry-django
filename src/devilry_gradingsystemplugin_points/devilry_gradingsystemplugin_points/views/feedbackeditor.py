from django.views.generic import FormView
from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Submit
from crispy_forms.layout import Field

from devilry_gradingsystem.views.feedbackeditorbase import FeedbackEditorMixin


class FeedbackEditorFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self.last_draft = kwargs.pop('last_draft')
        super(FeedbackEditorFormBase, self).__init__(*args, **kwargs)
        self._add_feedbacktext_field()

    def _add_feedbacktext_field(self):
        if self.last_draft:
            feedbacktext_editor = self.last_draft.feedbacktext_editor
        else:
            feedbacktext_editor = FeedbackDraft.DEFAULT_FEEDBACKTEXT_EDITOR
        self.fields['feedbacktext'] = forms.CharField(widget=forms.Textarea)


class FeedbackEditorFormView(FeedbackEditorMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super(PointsFeedbackEditorView, self).get_form_kwargs()
        kwargs['last_draft'] = self.last_draft
        return kwargs

    def get(self, *args, **kwargs):
        self.set_delivery_and_last_draft()
        return super(PointsFeedbackEditorView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.set_delivery_and_last_draft()
        return super(PointsFeedbackEditorView, self).get(*args, **kwargs)




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
                Submit('save-draft', _('Save draft')),
                Submit('publish', _('Publish'))
            )
        )


class PointsFeedbackEditorView(FeedbackEditorFormView):
    template_name = 'devilry_gradingsystemplugin_points/feedbackeditor.django.html'
    form_class = PointsFeedbackEditorForm


    # def form_valid(self, form):
    #     return super(PointsFeedbackEditorView, self).form_valid(form)