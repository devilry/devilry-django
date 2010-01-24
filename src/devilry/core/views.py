from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from models import DeliveryCandidate, FileMeta
from django.forms.models import inlineformset_factory
from datetime import datetime


def dashboard(request):
    return HttpResponse('Should display a listing of courses and stuff like that!')


class DeliveryCandidateForm(forms.ModelForm):
    class Meta:
        model = DeliveryCandidate
        exclude = ['time_of_delivery']


FileMetaForm = inlineformset_factory(DeliveryCandidate, FileMeta)


def deliver(request):
    if request.method == 'POST':
        if 'add_file' in request.POST:
            print "Add file..."
        else:
            print 'Deliver...'

        form = DeliveryCandidateForm(request.POST)
        formset = FileMetaForm(request.POST, request.FILES, instance=form.instance)
        print dir(formset)

        
        for f in formset.forms:
            #print dir(f)
            print f.has_changed()
        if form.is_valid() and formset.is_valid():
            form.instance.time_of_delivery = datetime.now()
            #form.save()
            #formset.save()
            return HttpResponse('thanks')
            #return HttpResponseRedirect('thanks')
    else:
        form = DeliveryCandidateForm()
        #print dir(form.instance)
        formset = FileMetaForm()
        #print dir(formset)
    return render_to_response('core/delivery.html', {
        'form': form,
        'formset': formset,
    })
