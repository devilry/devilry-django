

from django import forms
from django.utils.translation import pgettext_lazy
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from cradmin_legacy.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment


class AssignmentAnonymizationmodeUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    fields = ['anonymizationmode']
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'

    def __get_anonymizationmode_choices(self):
        return [
            (
                Assignment.ANONYMIZATIONMODE_OFF,
                Assignment.ANONYMIZATIONMODE_CHOICES_DICT[Assignment.ANONYMIZATIONMODE_OFF]
            ),
            (
                Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                Assignment.ANONYMIZATIONMODE_CHOICES_DICT[Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS]
            ),
        ]

    def get_form(self, form_class=None):
        form = super(AssignmentAnonymizationmodeUpdateView, self).get_form()
        form.fields['anonymizationmode'].widget = forms.RadioSelect()
        form.fields['anonymizationmode'].choices = self.__get_anonymizationmode_choices()
        return form

    def get_pagetitle(self):
        return pgettext_lazy('assignment config', "Edit anonymization settings")

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)

    def post(self, request, *args, **kwargs):
        self._old_anonymization_mode = self.get_object().anonymizationmode
        return super(AssignmentAnonymizationmodeUpdateView, self).post(request, *args, **kwargs)

    def get_success_message(self, object):
        assignment = object
        old_anonymizationmode = Assignment.ANONYMIZATIONMODE_CHOICES_SHORT_LABEL_DICT[self._old_anonymization_mode]
        new_anonymizationmode = Assignment.ANONYMIZATIONMODE_CHOICES_SHORT_LABEL_DICT[assignment.anonymizationmode]
        return pgettext_lazy(
            'assignment config',
            'Changed anonymization mode from "%(old_anonymizationmode)s" '
            'to "%(new_anonymizationmode)s".'
        ) % {
            'old_anonymizationmode': old_anonymizationmode,
            'new_anonymizationmode': new_anonymizationmode
        }

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentAnonymizationmodeUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
