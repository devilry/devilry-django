from django.contrib.auth.decorators import login_required
from devilry.core.models import Delivery
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

@login_required
def list_deliveries(request):
    return render_to_response('devilry/studentview/list_deliveries.django.html', {
        'deliveries': Delivery.where_is_student(request.user),
        }, context_instance=RequestContext(request))

@login_required
def show_delivery(request, delivery_id):
    return render_to_response('devilry/studentview/show_delivery.django.html', {
        'delivery': get_object_or_404(Delivery, pk=delivery_id),
        }, context_instance=RequestContext(request))
