from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404

from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
from devilry_gradingsystem.models import FeedbackDraft


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
        draft = self.get_feedbackdraft()
        delivery = self.object
        context['unsaved_staticfeedback'] = draft.to_staticfeedback()
        return context