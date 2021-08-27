

from django import forms
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers.crudbase import OnlySaveButtonMixin
from cradmin_legacy.viewhelpers.update import UpdateView
from cradmin_legacy.widgets.datetimepicker import DateTimePickerWidget

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
        self.fields['first_deadline'].label = gettext_lazy('First deadline')

    def clean_first_deadline(self):
        first_deadline = self.cleaned_data.get('first_deadline', None)
        if first_deadline:
            first_deadline = first_deadline.replace(second=59)
        return first_deadline
    
    def clean(self):
        return super().clean()


class AssignmentFirstDeadlineUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment
    template_name = 'devilry_cradmin/viewhelpers/devilry_updateview_with_backlink.django.html'
    fields = [
        'first_deadline'
    ]

    def get_form_class(self):
        return AssignmentFirstDeadlineForm

    def get_pagetitle(self):
        return gettext_lazy('Edit first deadline')

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentFirstDeadlineUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
