from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, HTML

from devilry.apps.core.models import Assignment
from devilry_examiner.views.add_deadline import DevilryDatetimeFormField


class AssignmentUpdateForm(forms.ModelForm):
    publishing_time = DevilryDatetimeFormField(
        label=_('Publishing time'),
        help_text=_('The time when the assignment is to be published (visible to students and examiners). Format: "YYYY-MM-DD hh:mm".'),
    )

    class Meta:
        model = Assignment
        fields = ['long_name', 'short_name', 'publishing_time', 'anonymous', 'deadline_handling']


    def __init__(self, *args, **kwargs):
        super(AssignmentUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('long_name', css_class='input-lg'),
            'publishing_time',
            'anonymous',
            'deadline_handling',
            HTML('<div class="alert alert-warning">'),
            'short_name',
            HTML('</div>'),
            HTML('<hr>'),
            ButtonHolder(
                Submit('submit', _('Save'), css_class='btn-lg')
            )
        )


class AssignmentUpdateView(UpdateView):
    model = Assignment
    template_name = 'devilry_subjectadmin/assignment_update_form.django.html'
    form_class = AssignmentUpdateForm
    pk_url_kwarg = 'id'
    context_object_name = 'assignment'

    def get_success_url(self):
        return reverse('devilry_subjectadmin_assignment', kwargs=self.kwargs)

    def get_queryset(self):
        return Assignment.where_is_admin_or_superadmin(self.request.user)