from django.utils.translation import pgettext_lazy
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from cradmin_legacy.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentExaminerSelfAssignUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'
    fields = ['examiners_can_self_assign', 'examiner_self_assign_limit']

    def get_pagetitle(self):
        return pgettext_lazy(
            'admin examiner selfassign setting',
            'Edit examiner self-assign'
        )

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentExaminerSelfAssignUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
    
    def post(self, request, *args, **kwargs):
        self._old_selfassign_enabled_value = self.get_object().examiners_can_self_assign
        self._old_selfassign_limit_value = self.get_object().examiner_self_assign_limit
        return super(AssignmentExaminerSelfAssignUpdateView, self).post(request, *args, **kwargs)

    def get_success_message(self, object):
        assignment = object
        success_message = None
        if assignment.examiners_can_self_assign and self._old_selfassign_enabled_value:
            if assignment.examiner_self_assign_limit != self._old_selfassign_limit_value:
                success_message = pgettext_lazy(
                    'admin examiner selfassign setting',
                    'Examiner self-assign limit changed from %(old_limit)s to %(new_limit)s.'
                ) % {
                    'old_limit': self._old_selfassign_limit_value,
                    'new_limit': assignment.examiner_self_assign_limit
                }
        elif assignment.examiners_can_self_assign:
            # Enabled
            success_message = pgettext_lazy(
                'admin examiner selfassign setting',
                'Examiner self-assign enabled with self-assign limit set to %(limit)s.'
            ) % {
                'limit': assignment.examiner_self_assign_limit
            }
        else:
            # Disabled
            success_message = pgettext_lazy(
                'admin examiner selfassign setting',
                'Examiner self-assign disabled.'
            )

        return success_message
