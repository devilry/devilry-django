from __future__ import unicode_literals

from django_cradmin.viewhelpers.update import UpdateView
from django.utils.translation import ugettext_lazy as _, pgettext_lazy, ugettext_lazy

from devilry.apps.core import models as coremodels


class AssignmentAnonymizationmodeUpdateView(UpdateView):
    model = coremodels.Assignment

    fields = ['anonymizationmode']

    def get_pagetitle(self):
        return pgettext_lazy('assignment config', "Edit anonymization settings")

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)
