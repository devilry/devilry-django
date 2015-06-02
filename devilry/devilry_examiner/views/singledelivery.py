from django.views.generic import DetailView
from django.shortcuts import redirect
#from django.http import Http404

from devilry.apps.core.models import Delivery
from devilry.devilry_examiner.views.singlegroupoverview import get_previous_and_next_group_waiting_for_feedback
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile
from devilry.devilry_gradingsystem.views.feedbackdraft_preview import StaticFeedbackPreviewMock


class SingleDeliveryView(DetailView):
    template_name = "devilry_examiner/singledelivery.django.html"
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

    def get(self, *args, **kwargs):
        edit_feedback = self.request.GET.get('edit_feedback', False) == 'true'
        if edit_feedback:
            delivery = self.get_object()
            assignment = delivery.assignment
            if assignment.has_valid_grading_setup():
                return redirect(assignment.get_gradingsystem_plugin_api().get_edit_feedback_url(delivery.id))

        return super(SingleDeliveryView, self).get(*args, **kwargs)

    def __add_last_feedbackdraft_to_context_data(self, context, delivery):
        last_feedbackdraft = FeedbackDraft.get_last_feedbackdraft(
            assignment=delivery.assignment,
            delivery=delivery,
            user=self.request.user)
        if last_feedbackdraft:
            if delivery.last_feedback and last_feedbackdraft.staticfeedback == delivery.last_feedback:
                return  # No need to show the draft if it is the same as the published feedback
            context['last_feedbackdraft'] = last_feedbackdraft
            draftfiles = FeedbackDraftFile.objects.filter_accessible_files(
                user=self.request.user, delivery=delivery, assignment=delivery.assignment)
            unsaved_staticfeedback = last_feedbackdraft.to_staticfeedback()
            staticfeedbackmock = StaticFeedbackPreviewMock(
                rendered_view=unsaved_staticfeedback.rendered_view,
                grade=unsaved_staticfeedback.grade,
                is_passing_grade=unsaved_staticfeedback.is_passing_grade,
                # We send in a FeedbackDraftFile queryset. This works because it
                # has the same attributes as StaticFeedbackFileAttachment.
                files=draftfiles)
            context['last_feedbackdraft_staticfeedbackmock'] = staticfeedbackmock

    def get_context_data(self, **kwargs):
        context = super(SingleDeliveryView, self).get_context_data(**kwargs)
        delivery = self.object
        context['valid_grading_system_setup'] = delivery.assignment.has_valid_grading_setup()
        previous, next = get_previous_and_next_group_waiting_for_feedback(
            self.request.user, delivery.assignment_group)
        context['previous_group_waiting_for_feedback'] = previous
        context['next_group_waiting_for_feedback'] = next
        self.__add_last_feedbackdraft_to_context_data(context=context, delivery=delivery)
        return context
