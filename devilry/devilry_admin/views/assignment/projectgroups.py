from __future__ import unicode_literals

from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin
from django_cradmin.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentProjectGroupUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment

    fields = ['students_can_create_groups', 'students_can_not_create_groups_after']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)
