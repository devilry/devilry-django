from django.views.generic import View
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from devilry.apps.core.models import AssignmentGroup



class LastDeliveryOrGroupOverviewRedirectView(View):
    def get(self, request, groupid):
        group = get_object_or_404(AssignmentGroup, id=groupid)
        if group.last_delivery:
            return redirect('devilry_examiner_singledeliveryview', deliveryid=group.last_delivery.id)
        else:
            return redirect('devilry_examiner_singlegroupoverview', groupid=group.id)