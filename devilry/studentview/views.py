from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from devilry.core.models import Delivery, AssignmentGroup

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


class UploadFileForm(forms.Form):
    file = forms.FileField()

@login_required
def add_delivery(request, assignment_group_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    delivery_id = request.session.get('add_delivery-delivery_id')
    if request.method == 'POST':
        if delivery_id:
            delivery = get_object_or_404(Delivery, id=delivery_id)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            for chunk in f.chunks():
                print chunk
    else:
        if delivery_id:
            del request.session['add_delivery-delivery_id']
        form = UploadFileForm()
    return render_to_response('devilry/studentview/add_delivery.django.html', {
        'assignment_group': assignment_group,
        'form': form,
        }, context_instance=RequestContext(request))
