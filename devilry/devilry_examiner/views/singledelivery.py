from django.views.generic import DetailView
from django.shortcuts import redirect
#from django.http import Http404

from devilry.apps.core.models import Delivery
from devilry.devilry_examiner.views.singlegroupoverview import get_previous_and_next_group_waiting_for_feedback


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


    def get_context_data(self, **kwargs):
        context = super(SingleDeliveryView, self).get_context_data(**kwargs)
        delivery = self.object
        context['valid_grading_system_setup'] = delivery.assignment.has_valid_grading_setup()
        previous, next = get_previous_and_next_group_waiting_for_feedback(
            self.request.user, delivery.assignment_group)
        context['previous_group_waiting_for_feedback'] = previous
        context['next_group_waiting_for_feedback'] = next
        return context
