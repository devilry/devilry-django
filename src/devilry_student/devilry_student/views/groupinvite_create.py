from django.views.generic.edit import FormView
from django.utils.translation import ugettext_lazy as _
from django import forms


class CreateForm(forms.Form):
    send_to = forms.CharField(
        label=_('Send invite to'),
        help_text=_('The username of the student you want to invite to your group.'))


class GroupInviteShowView(FormView):
    template_name = 'devilry_student/groupinvite_create.django.html'

    def form_valid(self):

        pass


    # def get_group(self):
    #     return get_object_or_404(AssignmentGroup.objects.filter_, )

    def get_context_data(self):
        pass