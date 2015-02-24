from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404

from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile


class FeedbackDraftPreviewView(DetailView):
    template_name = "devilry_gradingsystem/feedbackdraft_preview.django.html"
    model = Delivery
    pk_url_kwarg = 'deliveryid'
    context_object_name = 'delivery'

    def get_queryset(self):
        return Delivery.objects.filter_examiner_has_access(self.request.user)\
            .select_related( # Use select_related to lookup all the related objects in the query
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode', # Assignment
                'deadline__assignment_group__parentnode__parentnode', # Period
                'deadline__assignment_group__parentnode__parentnode__parentnode', # Subject
                )

    def get_feedbackdraft(self):
        delivery = self.object
        draftid = self.kwargs['draftid']
        try:
            return FeedbackDraft.objects.get(
                delivery=delivery,
                id=draftid)
        except FeedbackDraft.DoesNotExist:
            raise Http404('Feedback draft with ID={} does not exist.'.format(draftid))

    def get_context_data(self, **kwargs):
        context = super(FeedbackDraftPreviewView, self).get_context_data(**kwargs)
        delivery = context['object']
        draft = self.get_feedbackdraft()
        context['unsaved_staticfeedback'] = draft.to_staticfeedback()
        context['valid_grading_system_setup'] = True
        feedback_fileattachments = FeedbackDraftFile.objects.filter(
            saved_by=self.request.user, delivery=delivery)
        context['feedback_fileattachments'] = feedback_fileattachments
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        delivery = self.object
        if 'submit_publish' in self.request.POST:
            draft = self.get_feedbackdraft()
            draft.published = True
            draft.staticfeedback = draft.to_staticfeedback()
            draft.staticfeedback.full_clean()
            draft.staticfeedback.save()
            return redirect('devilry_examiner_singledeliveryview', deliveryid=delivery.id)
        else:
            return redirect(delivery.assignment.get_gradingsystem_plugin_api().get_edit_feedback_url(delivery.id))
