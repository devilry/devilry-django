from __future__ import unicode_literals

from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin
from django_cradmin.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentFirstDeadlineUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment

    fields = ['first_deadline']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])
