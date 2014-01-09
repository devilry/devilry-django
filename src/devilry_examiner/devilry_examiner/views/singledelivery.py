from django.views.generic import DetailView
#from django.http import Http404

from devilry.apps.core.models import Delivery


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

    def get_context_data(self, **kwargs):
        context = super(SingleDeliveryView, self).get_context_data(**kwargs)
        delivery = self.object

        edit_feedback = False
        if delivery.last_feedback is None:
            edit_feedback = True
        elif delivery.last_feedback and self.request.GET.get('edit_feedback', False) == 'true':
            edit_feedback = True
        if edit_feedback:
            # TODO: Redirect to edit feedback view of the current grading system
            pass
        return context