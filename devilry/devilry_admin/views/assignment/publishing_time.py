from __future__ import unicode_literals

from django_cradmin.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentPublishingTimeUpdateView(UpdateView):
    model = coremodels.Assignment

    fields = ['publishing_time']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])
