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

    print request.user
    print dir(Delivery.objects.all()[0])
    print Delivery.objects.filter(deliverystudent__student=request.user)
    class DeliveryCandidateForm(forms.ModelForm):
        delivery = forms.ModelChoiceField(
                queryset=Delivery.objects.all())
                #queryset=Delivery.objects.filter(students=request.user))
        
        class Meta:
            model = DeliveryCandidate
            exclude = ['time_of_delivery']

    if request.method == 'POST':
        if 'add_file' in request.POST:
            print "Add file..."
        else:
            print 'Deliver...'

        form = DeliveryCandidateForm(request.POST)
        formset = FileMetaForm(request.POST, request.FILES, instance=form.instance)
        print dir(formset)

        if form.is_valid() and formset.is_valid():
            form.instance.time_of_delivery = datetime.now()
            form.save()
            formset.save()
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
