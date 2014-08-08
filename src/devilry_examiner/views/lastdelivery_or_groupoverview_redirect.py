from django.views.generic import View
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from devilry.apps.core.models import AssignmentGroup



class LastDeliveryOrGroupOverviewRedirectView(View):
    def get(self, request, groupid):
        group = get_object_or_404(AssignmentGroup, id=groupid)
        if group.last_delivery:
            url = reverse('devilry_examiner_singledeliveryview', args=[group.last_delivery.id])
            edit_feedback = self.request.GET.get('edit_feedback', False) == 'true'
            if edit_feedback:
                url = '{}?edit_feedback=true'.format(url)
            return redirect(url)
        else:
            return redirect('devilry_examiner_singlegroupoverview', groupid=group.id)