from datetime import datetime
from random import randint

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django import forms
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest

from devilry.devilry_markup.parse_markdown import markdown_full
from devilry.devilry_gradingsystem.models import FeedbackDraft
from devilry.devilry_gradingsystem.widgets.editmarkdown import EditMarkdownLayoutObject
from devilry.devilry_gradingsystem.widgets.editfeedbackbuttonbar import BulkEditFeedbackButtonBar
from devilry.devilry_examiner.views.bulkviewbase import BulkViewBase
from devilry.devilry_examiner.views.bulkviewbase import OptionsForm


class FeedbackBulkEditorOptionsForm(OptionsForm):
    draft_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput)

    def clean_draft_id(self):
        draft_id = self.cleaned_data['draft_id']
        if draft_id is not None and not FeedbackDraft.objects.filter(id=draft_id).exists():
            raise forms.ValidationError("Invalid draft ID: {}.".format(draft_id))
        return draft_id

    def clean(self):
        cleaned_data = super(FeedbackBulkEditorOptionsForm, self).clean()
        if hasattr(self, 'cleaned_groups'):
            cleaned_groups = self.cleaned_groups
            groups_with_no_deliveries = cleaned_groups.exclude_groups_with_deliveries()
            if groups_with_no_deliveries.exists():
                raise forms.ValidationError(_('One or more of the selected groups has no deliveries.'))
            else:
                self.cleaned_groups = cleaned_groups
        return cleaned_data


class FeedbackBulkEditorFormBase(FeedbackBulkEditorOptionsForm):
    def __init__(self, *args, **kwargs):
        super(FeedbackBulkEditorFormBase, self).__init__(*args, **kwargs)
        self._add_feedbacktext_field()

    def _add_feedbacktext_field(self):
        self.fields['feedbacktext'] = forms.CharField(
            label=_('Feedback text'),
            required=False)

    def get_feedbacktext_layout_elements(self):
        return [EditMarkdownLayoutObject()]

    def get_submitbuttons_layout_elements(self):
        return [BulkEditFeedbackButtonBar()]

    def add_common_layout_elements(self):
        for element in self.get_feedbacktext_layout_elements():
            self.helper.layout.append(element)
        for element in self.get_submitbuttons_layout_elements():
            self.helper.layout.append(element)
        self.helper.layout.append('group_ids')
        self.helper.layout.append('draft_id')


class FeedbackBulkEditorFormView(BulkViewBase):
    optionsform_class = FeedbackBulkEditorOptionsForm

    def get_primaryform_classes(self):
        return {
            'submit_publish': self.form_class,
            'submit_preview': self.form_class,
        }

    def get_points_from_form(self, form):
        raise NotImplementedError()

    def get_default_points_value(self):
        raise NotImplementedError()

    def optionsform_invalid(self, optionsform):
        return self.render_view({
            'optionsform': optionsform
        })

    def get_create_feedbackdraft_kwargs(self, form, publish):
        return {
            'groups': form.cleaned_groups,
            'feedbacktext_raw': form.cleaned_data['feedbacktext'],
            'feedbacktext_html': markdown_full(form.cleaned_data['feedbacktext']),
            'publish': publish,
            'points': self.get_points_from_form(form)
        }

    def _get_preview_redirect_url(self, randomkey):
        return "{}".format(reverse('devilry_gradingsystem_feedbackdraft_bulkpreview',
                                   kwargs={'assignmentid': self.object.id, 'randomkey': randomkey}))

    def save_pluginspecific_state(self, form):
        """
        Save extra state that is specific to this plugin. I.E: Input from
        users that has no corresponding field in FeedbackDraft, and has to be
        stored in the data models for the plugin.
        """
        pass

    def submitted_primaryform_valid(self, form, context_data):
        publish = 'submit_publish' in self.request.POST
        preview = 'submit_preview' in self.request.POST

        self.save_pluginspecific_state(form)
        draft_ids = self.create_feedbackdrafts(**self.get_create_feedbackdraft_kwargs(form, publish))
        if preview:
            randomkey = '{}.{}'.format(timezone.now().strftime('%Y-%m-%d_%H-%M-%S-%f'), randint(0, 10000000))
            sessionkey = 'devilry_gradingsystem_draftids_{}'.format(randomkey)
            self.request.session[sessionkey] = draft_ids
            return redirect(self._get_preview_redirect_url(randomkey))
        else:
            return super(FeedbackBulkEditorFormView, self).submitted_primaryform_valid(form, context_data)

    def get_initial_from_draft(self, draft):
        return {
            'feedbacktext': draft.feedbacktext_raw
        }

    def get_primaryform_initial_data(self, formclass):
        if self.optionsdict['draft_id']:
            draft = FeedbackDraft.objects.get(id=self.optionsdict['draft_id'])
            if draft.delivery.assignment != self.assignment:
                raise Http404()
            extra_data = self.get_initial_from_draft(draft)
        else:
            extra_data = {
                'feedbacktext': '',
                'points': self.get_default_points_value()
            }
        initial = super(FeedbackBulkEditorFormView, self).get_primaryform_initial_data(formclass)
        extra_data.update(initial)
        return extra_data

    def get(self, *args, **kwargs):
        assignment = self.get_object()
        if not assignment.has_valid_grading_setup():
            return redirect('devilry_examiner_singledeliveryview', deliveryid=self.delivery.id)
        return super(FeedbackBulkEditorFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        assignment = self.get_object()
        if not assignment.has_valid_grading_setup():
            return HttpResponseBadRequest('Grading system is not set up correctly')
        elif 'submit_save_draft' in self.request.POST:
            return redirect(self.request.path)
        return super(FeedbackBulkEditorFormView, self).post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FeedbackBulkEditorFormView, self).get_context_data(**kwargs)
        assignment = self.object
        context['valid_grading_system_setup'] = assignment.has_valid_grading_setup()
        return context

    def create_feedbackdrafts(self, groups, points, feedbacktext_raw, feedbacktext_html, publish=False):
        draft_ids = []
        for group in groups:
            delivery_id = group.last_delivery_id
            draft = FeedbackDraft(
                delivery_id=delivery_id,
                points=points,
                feedbacktext_raw=feedbacktext_raw,
                feedbacktext_html=feedbacktext_html,
                saved_by=self.request.user
            )
            if publish:
                draft.published = True
                draft.staticfeedback = draft.to_staticfeedback()
                draft.staticfeedback.full_clean()
                draft.staticfeedback.save()
            draft.save()
            draft_ids.append(draft.id)
        return draft_ids
