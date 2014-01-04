from django.views.generic import DetailView
#from django.http import Http404

from devilry.apps.core.models import Delivery


class SingleDeliveryView(DetailView):
    template_name = "devilry_examiner/singledeliveryview.django.html"
    model = Delivery
    pk_url_kwarg = 'deliveryid'
    context_object_name = 'delivery'

    def get_queryset(self):
        return Delivery.objects.filter_examiner_has_access(self.request.user)