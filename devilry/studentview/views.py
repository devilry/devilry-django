from os.path import basename
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from devilry.core.models import Delivery, AssignmentGroup
from devilry.core.widgets import ReadOnlyWidget


@login_required
def list_deliveries(request):
    return render_to_response('devilry/studentview/list_deliveries.django.html', {
        'deliveries': Delivery.where_is_student(request.user),
        }, context_instance=RequestContext(request))

@login_required
def show_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/show_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))



class ExistingFileForm(forms.Form):
    filename = forms.CharField(widget=ReadOnlyWidget)
ExistingFileFormSet = formset_factory(ExistingFileForm, extra=0, can_delete=True)

class UploadFileForm(forms.Form):
    file = forms.FileField()
UploadFileFormSet = formset_factory(UploadFileForm, extra=1)

@login_required
def add_delivery(request, assignment_group_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    if not assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    sessionkey = 'add_delivery-delivery_id'
    delivery_id = request.session.get(sessionkey)
    if request.method == 'POST':
        if delivery_id:
            delivery = get_object_or_404(Delivery, id=delivery_id)
        else:
            delivery = Delivery.begin(assignment_group)
        formset = UploadFileFormSet(request.POST, request.FILES, prefix='upload')
        if formset.is_valid():
            for f in request.FILES.values():
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

        if 'delete' in request.POST:
            existing_formset = ExistingFileFormSet(request.POST, prefix='existing')
            if existing_formset.is_valid():
                try:
                    for form in existing_formset.deleted_forms:
                        filename = form.cleaned_data['filename']
                        Delivery.store.remove(delivery, filename)
                except AttributeError, e:
                    # This is a workaround for deleting the last file in the formset.
                    # see: http://code.djangoproject.com/ticket/10828
                    Delivery.store.clear(delivery)

        request.session[sessionkey] = delivery.id
        existing = [{'filename': filename}
                for filename in Delivery.store.filenames(delivery)]
        existing_formset = ExistingFileFormSet(initial=existing, prefix='existing')
    else:
        if delivery_id:
            del request.session[sessionkey]
        formset = UploadFileFormSet(prefix='upload')
        existing_formset = ExistingFileFormSet(prefix='existing')

    return render_to_response('devilry/studentview/add_delivery.django.html', {
        'assignment_group': assignment_group,
        'formset': formset,
        'existing_formset': existing_formset,
        }, context_instance=RequestContext(request))


@login_required
def successful_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/successful_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))
