from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.apps.core.models import Delivery


@login_required
def show_delivery(request, delivery_id):
    try:
        delivery = Delivery.objects\
            .select_related('deadline', 'deadline__assignment_group')\
            .get(id=delivery_id)
    except Delivery.DoesNotExist, e:
        raise Http404()
    else:
        return HttpResponseRedirect(
            reverse_cradmin_url(
                instanceid='devilry_student_group',
                appname='deliveries',
                roleid=delivery.assignment_group.id,
                viewname='deliverydetails',
                kwargs={'pk': delivery.id}))
