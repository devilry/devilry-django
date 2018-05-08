from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin
from django_cradmin.viewhelpers.update import UpdateView
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core import models as coremodels


class AssignmentFirstDeadlineForm(forms.ModelForm):
    class Meta:
        model = coremodels.Assignment
        fields = [
            'first_deadline'
        ]

    def __init__(self, *args, **kwargs):
        super(AssignmentFirstDeadlineForm, self).__init__(*args, **kwargs)
        self.fields['first_deadline'].widget = DateTimePickerWidget()
        self.fields['first_deadline'].label = ugettext_lazy('First deadline')


class AssignmentFirstDeadlineUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'
    fields = [
        'first_deadline'
    ]

    def get_form_class(self):
        return AssignmentFirstDeadlineForm

    def get_pagetitle(self):
        return ugettext_lazy('Edit first deadline')

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentFirstDeadlineUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
