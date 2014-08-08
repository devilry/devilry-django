from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import get_object_or_404

from devilry.apps.core.models import AssignmentGroup


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