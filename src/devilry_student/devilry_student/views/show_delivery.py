from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.core.urlresolvers import reverse

from devilry.apps.core.models import Delivery


@login_required
def show_delivery(request, delivery_id):
    try:
        delivery = Delivery.objects.select_related('deadline').get(id=delivery_id)
    except Delivery.DoesNotExist, e:
        raise Http404()

    redirect_url = '{0}#/group/{1}/{2}'.format(reverse('devilry_student'),
                                               delivery.deadline.assignment_group_id,
                                               delivery.id)
    return render(request, 'devilry_student/show_delivery.django.html',
                  {"redirect_url": redirect_url},
                  content_type="text/html")
