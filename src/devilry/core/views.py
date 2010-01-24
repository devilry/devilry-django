from django.http import HttpResponse, HttpResponseRedirect
from django import forms


def dashboard(request):
    return HttpResponse('Should display a listing of courses and stuff like that!')


class DeliveryForm(forms.Form):
    pass
    #subject = forms.CharField(max_length=100)


def deliver(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('thanks')
    else:
        form = DeliveryForm()
    return render_to_response('devilry/core/deliver.html', {
        'form': form,
    })
