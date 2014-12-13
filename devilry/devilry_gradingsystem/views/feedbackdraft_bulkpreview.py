from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404
from django.utils.http import urlencode
from crispy_forms.helper import FormHelper

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import StaticFeedback
from devilry.devilry_gradingsystem.models import FeedbackDraft
from .feedbackbulkeditorbase import FeedbackBulkEditorOptionsForm



class EditDraftForm(FeedbackBulkEditorOptionsForm):
    def __init__(self, *args, **kwargs):
        super(EditDraftForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class FeedbackDraftBulkPreviewView(DetailView):
    template_name = "devilry_gradingsystem/feedbackdraft_bulkpreview.django.html"
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def get_object(self):
        assignment = super(FeedbackDraftBulkPreviewView, self).get_object()
        return assignment

    def _get_sessionkey(self):
        randomkey = self.kwargs['randomkey']
        return 'devilry_gradingsystem_draftids_{}'.format(randomkey)

    def _get_drafts(self):
        draft_ids = self.request.session[self._get_sessionkey()]
        drafts = FeedbackDraft.objects.filter(id__in=draft_ids)
        return drafts

    def get_context_data(self, **kwargs):
        context = super(FeedbackDraftBulkPreviewView, self).get_context_data(**kwargs)
        assignment = self.object

        drafts = list(self._get_drafts().select_related(
            'delivery', 'delivery__deadline', 'delivery__deadline__assignment_group'))

        draft = drafts[0]
        context['unsaved_staticfeedback'] = draft.to_staticfeedback()
        context['valid_grading_system_setup'] = self.object.has_valid_grading_setup()

        group_ids = [draft.delivery.assignment_group.id for draft in drafts]
        edit_draft_form = EditDraftForm(
            user=self.request.user,
            assignment=assignment,
            initial={
                'group_ids': group_ids,
                'draft_id': drafts[0].id}
        )
        context['edit_draft_form'] = edit_draft_form
        context['edit_draft_form_url'] = assignment.get_gradingsystem_plugin_api().get_bulkedit_feedback_url(assignment.id)

        return context

    def post(self, request, assignmentid, randomkey, *args, **kwargs):
        self.object = self.get_object()
        assignment = self.object

        drafts = self._get_drafts()
        del self.request.session[self._get_sessionkey()]
        for draft in drafts:
            draft.published = True
            draft.staticfeedback = draft.to_staticfeedback()
            draft.staticfeedback.full_clean()
            draft.staticfeedback.save()
            draft.save()
        return redirect('devilry_examiner_allgroupsoverview', assignmentid=assignment.id)
