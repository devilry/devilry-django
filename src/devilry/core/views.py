from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from models import DeliveryCandidate, FileMeta
from django.forms.models import inlineformset_factory


def dashboard(request):
    return HttpResponse('Should display a listing of courses and stuff like that!')


class DeliveryCandidateForm(forms.ModelForm):
    class Meta:
        model = DeliveryCandidate
        exclude = ['time_of_delivery']


FileMetaForm = inlineformset_factory(DeliveryCandidate, FileMeta)


def deliver(request):
    if request.method == 'POST':
        #form = DeliveryForm(request.POST)
        #if form.is_valid():
        #    return HttpResponseRedirect('thanks')
        pass
    else:
        i = DeliveryCandidate.objects.get(id=1)
        form = DeliveryCandidateForm(instance=i)
        formset = FileMetaForm(instance=i)
        print dir(formset)
    return render_to_response('core/delivery.html', {
        'form': form,
        'formset': formset,
    })
