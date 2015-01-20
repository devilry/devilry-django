from django.views.generic import View
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from devilry.apps.core.models import AssignmentGroup



class LastDeliveryOrGroupOverviewRedirectView(View):
    def get(self, request, groupid):
        queryset = AssignmentGroup.objects.annotate_with_last_delivery_id()
        group = get_object_or_404(queryset, id=groupid)
        if group.last_delivery_id is not None:
            url = reverse('devilry_examiner_singledeliveryview', args=[group.last_delivery_id])
            edit_feedback = self.request.GET.get('edit_feedback', False) == 'true'
            if edit_feedback:
                url = '{}?edit_feedback=true'.format(url)
            return redirect(url)
        else:
            return redirect('devilry_examiner_singlegroupoverview', groupid=group.id)
