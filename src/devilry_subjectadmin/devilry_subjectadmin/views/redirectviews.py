from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import get_object_or_404

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Delivery


class RedirectToSubjectAdminAppView(View):
    pathformat = None

    def get(self, request, **kwargs):
        path = self.pathformat.format(**kwargs)
        url = '{}?routeTo={}'.format(reverse('devilry_subjectadmin'), path)
        return HttpResponseRedirect(url)


class RedirectToGroupAdminAppView(View):
    def get(self, request, id):
        group = get_object_or_404(AssignmentGroup, id=id)
        path = '/assignment/{assignment.id}/@@manage-students/@@select/{group.id}'.format(
            assignment=group.assignment, group=group)
        url = '{}?routeTo={}'.format(reverse('devilry_subjectadmin'), path)
        return HttpResponseRedirect(url)


class RedirectToDeliveryAdminAppView(View):
    def get(self, request, id):
        queryset = Delivery.objects.select_related(
            'deadline',
            'deadline__assignment_group',
            'deadline__assignment_group__parentnode')
        delivery = get_object_or_404(queryset, id=id)
        path = '/assignment/{assignment.id}/@@manage-students/@@select-delivery/{group.id}/{delivery.id}'.format(
            assignment=delivery.assignment, group=delivery.assignment_group, delivery=delivery)
        url = '{}?routeTo={}'.format(reverse('devilry_subjectadmin'), path)
        return HttpResponseRedirect(url)
