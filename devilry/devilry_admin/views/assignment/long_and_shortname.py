

from cradmin_legacy.viewhelpers.update import UpdateView
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from devilry.apps.core import models as coremodels


class AssignmentLongAndShortNameUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment

    fields = ['long_name',
              'short_name']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])
