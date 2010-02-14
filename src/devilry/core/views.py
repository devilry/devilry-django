from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from models import DeliveryCandidate, FileMeta, Delivery
from django.forms.models import inlineformset_factory
from datetime import datetime
from django.contrib.auth.decorators import login_required


def dashboard(request):
    return HttpResponse('Should display a listing of courses and stuff like that!')


FileMetaForm = inlineformset_factory(DeliveryCandidate, FileMeta, extra=1)


@login_required
def deliver(request):

    class DeliveryCandidateForm(forms.ModelForm):
        #delivery = forms.ModelChoiceField(
                #queryset=Delivery.objects.all())
                ##queryset=Delivery.objects.filter(students=request.user))
        
        class Meta:
            model = DeliveryCandidate
            exclude = ['time_of_delivery']

    filemetas = []
    if request.method == 'POST':
        if 'add_file' in request.POST:
            print "Add file..."
        else:
            print 'Deliver...'

        form = DeliveryCandidateForm(request.POST)
        formset = FileMetaForm(request.POST, request.FILES, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            form.instance.time_of_delivery = datetime.now()
            deliverycandidate = form.save()
            filemetas = formset.save()
            if 'deliver' in request.POST:
                return HttpResponse('thanks')
                #return HttpResponseRedirect('thanks')
            else:
                form = DeliveryCandidateForm(deliverycandidate)
                formset = FileMetaForm(request.POST, request.FILES, instance=deliverycandidate)
    else:
        form = DeliveryCandidateForm()
        formset = FileMetaForm()
    return render_to_response('core/delivery.html', {
        'form': form,
        'formset': formset,
        'filemetas': filemetas
    })
