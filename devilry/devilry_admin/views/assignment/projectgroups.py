

from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from cradmin_legacy.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentProjectGroupUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'
    fields = ['students_can_create_groups', 'students_can_not_create_groups_after']

    def get_pagetitle(self):
        return gettext_lazy('Edit project group settings')

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentProjectGroupUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
