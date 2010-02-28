from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.db import models
from models import Delivery, FileMeta, DeliveryGroup
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.urlresolvers import reverse


def dashboard(request):
    return HttpResponse('Should display a listing of courses and stuff like that!')


FileMetaForm = inlineformset_factory(Delivery, FileMeta, extra=1)

class DeliveryCandidateForm(forms.ModelForm):
    class Meta:
        model = Delivery
        exclude = ['time_of_delivery', 'delivery']


@login_required
def deliver(request, deliveryid):
    filemetas = []
    if request.method == 'POST':
        delivery = DeliveryGroup.objects.get(id=deliveryid)
        #dc = Delivery(time_of_delivery = datetime.now(),
            #delivery=delivery)
        form = DeliveryCandidateForm(request.POST)
        form.instance.delivery = delivery
        formset = FileMetaForm(request.POST, request.FILES, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            form.instance.time_of_delivery = datetime.now()
            dc = form.save()
            filemetas = formset.save()
            if 'deliver' in request.POST:
                return HttpResponse('thanks')
               #return HttpResponseRedirect('thanks')
            else:
                form = DeliveryCandidateForm(request.POST, instance=dc)
                print form.instance.id
                formset = FileMetaForm(request.POST, request.FILES,
                    instance=dc)
    else:
        form = DeliveryCandidateForm()
        formset = FileMetaForm()
    return render_to_response('core/delivery.html', {
        'form': form,
        'formset': formset,
    })



def deliveryform(form, formset, url):
    return render_to_response('core/delivery.html', {
        'form': form,
        'formset': formset,
        'url': url
    })

@login_required
def start_delivery(request, deliveryid):
    form = DeliveryCandidateForm()
    formset = FileMetaForm()
    url = reverse('create-delivery', args=[deliveryid])
    return deliveryform(form, formset, url)

@login_required
def create_delivery(request, deliveryid, deliverycand_id=None):
    if request.method != 'POST' and deliverycand_id==None:
        raise Http404()

    delivery = get_object_or_404(DeliveryGroup, pk=deliveryid)
    form = DeliveryCandidateForm(request.POST)
    form = DeliveryCandidateForm(request.POST)
    if deliverycand_id != None:
        deliverycand = get_object_or_404(Delivery, pk=deliverycand_id)
        form.instance = deliverycand
    form.instance.delivery = delivery
    formset = FileMetaForm(request.POST, request.FILES, instance=form.instance)

    if form.is_valid() and formset.is_valid():
        form.instance.time_of_delivery = datetime.now()
        form.save()
        formset.save()
        if 'deliver' in request.POST:
            return HttpResponse('thanks')
        else:
            print dir(form.instance.filemeta_set)
            url = reverse('edit-delivery', args=[deliveryid, form.instance.pk])
            return deliveryform(form, formset, url)
    else:
        return deliveryform(form, formset)
