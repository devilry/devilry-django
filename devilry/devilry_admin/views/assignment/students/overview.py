from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy

from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core import models as coremodels


class Overview(listbuilderview.View):
    model = coremodels.AssignmentGroup
    template_name = 'devilry_admin/assignment/students/overview.django.html'

    def get_no_items_message(self):
        return ugettext_lazy('No students')

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignment'] = self.request.cradmin_role
        return context

    def get_queryset_for_role(self, role):
        assignment = role
        return coremodels.AssignmentGroup.objects\
            .filter(parentnode=assignment)\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=coremodels.Candidate.objects.select_related(
                                    'relatedstudent__user'),
                                to_attr='candidates'),
                models.Prefetch('examiners',
                                queryset=coremodels.Examiner.objects.select_related(
                                    'relatedexaminer__user'),
                                to_attr='examiners'))


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
