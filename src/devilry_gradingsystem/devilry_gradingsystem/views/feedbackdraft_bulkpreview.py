from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404
from django.utils.http import urlencode

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import StaticFeedback
from devilry_gradingsystem.models import FeedbackDraft
from .feedbackbulkeditorbase import FeedbackBulkEditorGroupIdsForm



class FeedbackDraftBulkPreviewView(DetailView):
    template_name = "devilry_gradingsystem/feedbackdraft_bulkpreview.django.html"
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def get_object(self):
        assignment = super(FeedbackDraftBulkPreviewView, self).get_object()
        if not 'selected_group_ids' in self.request.session:
            raise Http404
        else:
            selected_group_ids = self.request.session['selected_group_ids']
            form = FeedbackBulkEditorGroupIdsForm({
                'group_ids': selected_group_ids
            }, assignment=assignment, user=self.request.user)
            if form.is_valid():
                self.selected_groups = form.cleaned_groups
            else:
                raise Http404
        return assignment

    def get_feedbackdraft(self, draftid):
        try:
            return FeedbackDraft.objects.get(id=draftid)
        except FeedbackDraft.DoesNotExist:
            raise Http404('Feedback draft with ID={} does not exist.'.format(draftid))

    def get_context_data(self, **kwargs):
        context = super(FeedbackDraftBulkPreviewView, self).get_context_data(**kwargs)
        draft = self.get_feedbackdraft(self.kwargs['draftid'])
        # delivery = self.object
        context['unsaved_staticfeedback'] = draft.to_staticfeedback()
        context['valid_grading_system_setup'] = True
        print self.selected_groups
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        assignment = self.object
        print
        print self.kwargs
        print
        if 'submit_publish' in self.request.POST:
            for draftid in self.request.GET.getlist('draftid'):
                draft = self.get_feedbackdraft(draftid)
                draft.published = True
                draft.staticfeedback = draft.to_staticfeedback()
                draft.staticfeedback.full_clean()
                draft.staticfeedback.save()
            return redirect('devilry_examiner_allgroupsoverview', assignmentid=assignment.id)
        else:
            redirect_url = assignment.get_gradingsystem_plugin_api().get_bulkedit_feedback_url(assignment.id)
            redirect_url = redirect_url + '?' + urlencode({'edit': self.request.GET.getlist('edit')}, doseq=True) + '&draftid=' + self.kwargs['draftid']

            return redirect(redirect_url)
