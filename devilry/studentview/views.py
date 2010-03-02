from os.path import basename
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
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
    sessionkey = 'add_delivery-delivery_id'
    delivery_id = request.session.get(sessionkey)
    if request.method == 'POST':
        if delivery_id:
            delivery = get_object_or_404(Delivery, id=delivery_id)
        else:
            delivery = Delivery.begin(assignment_group)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            filename = basename(f.name) # do not think basename is needed, but at least we *know* we only get the filename.
            out = Delivery.store.write_open(delivery, filename)
            for chunk in f.chunks():
                out.write(chunk)
            out.close()
        if 'deliver' in request.POST:
            if delivery_id:
                del request.session[sessionkey]
            delivery.finish()
            return HttpResponseRedirect(reverse('successful-delivery', args=(delivery.id,)))
        else:
            request.session[sessionkey] = delivery.id
    else:
        if delivery_id:
            del request.session[sessionkey]
        form = UploadFileForm()
    return render_to_response('devilry/studentview/add_delivery.django.html', {
        'assignment_group': assignment_group,
        'form': form,
        }, context_instance=RequestContext(request))


@login_required
def successful_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    return render_to_response('devilry/studentview/successful_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))
