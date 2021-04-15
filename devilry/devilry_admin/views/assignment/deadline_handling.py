

from crispy_forms import layout
from django import forms
from django.http import Http404
from django.utils.translation import pgettext_lazy
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from cradmin_legacy.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import SubjectPermissionGroup


class AssignmentDeadlineHandlingUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    fields = ['deadline_handling']
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'

    def dispatch(self, request, *args, **kwargs):
        assignment = Assignment.objects.get(id=kwargs['pk'])
        subject = assignment.parentnode.parentnode
        user_devilry_role = SubjectPermissionGroup.objects\
            .get_devilryrole_for_user_on_subject(user=request.user, subject=subject)
        if user_devilry_role is None:
            raise Http404()
        return super(AssignmentDeadlineHandlingUpdateView, self).dispatch(request=request, *args, **kwargs)

    def __get_deadline_handling_choices(self):
        return [
            (
                Assignment.DEADLINEHANDLING_SOFT,
                pgettext_lazy('deadline handling update hard choice',
                              'SOFT. Students will be able to add upload deliveries and comment after '
                              'the deadline has expired, but this will be clearly highlighted. Deliveries made after '
                              'the deadline has expired might not be considered when an examiner is correcting '
                              'deliveries.')
            ),
            (
                Assignment.DEADLINEHANDLING_HARD,
                pgettext_lazy('deadline handling update hard choice',
                              'HARD. Students will not be able to upload deliveries or comment after the deadline has '
                              'expired. This can only be reverted by setting the deadline handling to soft, extending '
                              'the deadline or give a new attempt. A highlighted box will appear in the top of the '
                              'delivery feed informing the user that the assignment uses hard deadlines.')
            ),
        ]

    def get_form(self, form_class=None):
        form = super(AssignmentDeadlineHandlingUpdateView, self).get_form()
        form.fields['deadline_handling'].widget = forms.RadioSelect()
        form.fields['deadline_handling'].choices = self.__get_deadline_handling_choices()
        form.fields['deadline_handling'].help_text = None
        return form

    def get_pagetitle(self):
        return pgettext_lazy('assignment config', "Edit deadline handling")

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)

    def post(self, request, *args, **kwargs):
        self._old_deadline_handling = self.get_object().deadline_handling
        return super(AssignmentDeadlineHandlingUpdateView, self).post(request, *args, **kwargs)

    def get_deadline_handling_soft_text(self):
        return pgettext_lazy('deadline update view deadline soft text', 'SOFT')

    def get_deadline_handling_hard_text(self):
        return pgettext_lazy('deadline update view deadline hard text', 'HARD')

    def get_deadline_handling_text(self, assignment):
        if assignment.deadline_handling == 0:
            return self.get_deadline_handling_soft_text()
        return self.get_deadline_handling_hard_text()

    def get_success_message(self, object):
        assignment = object
        if self._old_deadline_handling == Assignment.DEADLINEHANDLING_SOFT:
            old_deadline_handling_text = self.get_deadline_handling_soft_text()
            new_deadline_handling_text = self.get_deadline_handling_text(assignment=assignment)
        else:
            old_deadline_handling_text = self.get_deadline_handling_hard_text()
            new_deadline_handling_text = self.get_deadline_handling_text(assignment=assignment)
        return pgettext_lazy(
            'assignment config',
            'Changed deadline handling from "%(old_deadline_handling_text)s" '
            'to "%(new_deadline_handling_text)s".'
        ) % {
            'old_deadline_handling_text': old_deadline_handling_text,
            'new_deadline_handling_text': new_deadline_handling_text
        }

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentDeadlineHandlingUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
