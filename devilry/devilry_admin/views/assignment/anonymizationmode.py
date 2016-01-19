from __future__ import unicode_literals

from django_cradmin.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentAnonymizationmodeUpdateView(UpdateView):
    model = coremodels.Assignment

    fields = ['anonymizationmode']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)
