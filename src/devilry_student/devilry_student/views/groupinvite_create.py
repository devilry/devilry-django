from django.views.generic.detail import DetailView
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, HTML

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import GroupInvite


class CreateForm(forms.ModelForm):
    sent_to = forms.CharField(
        label=_('Send invite to'),
        help_text=_('The username of the student you want to invite to your group.'))

    class Meta:
        model = AssignmentGroup
        fields = ['sent_to']

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        self.sent_by = kwargs.pop('sent_by', None)
        super(CreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'sent_to',
            ButtonHolder(
                Submit('submit', _('Send invite'))
            )
        )

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        sent_to_username = cleaned_data.get('sent_to')
        if sent_to_username:
            try:
                sent_to = User.objects.get(username=sent_to_username)
            except User.DoesNotExist:
                raise forms.ValidationError(_('No user with the given username exists.'))
            else:
                invite = GroupInvite(group=self.group, sent_by=self.sent_by, sent_to=sent_to)
                invite.full_clean()
        return cleaned_data


class GroupInviteCreateView(DetailView):
    template_name = 'devilry_student/groupinvite_create.django.html'
    pk_url_kwarg = 'group_id'
    context_object_name = 'group'

    def get_queryset(self):
        return AssignmentGroup.objects.filter_student_has_access(self.request.user)\
            .select_related(
                'parentnode', # Assignment
                'parentnode__parentnode', # Period
                'parentnode__parentnode__parentnode') # Subject

    def post(self, *args, **kwargs):
        group = self.get_object()
        form = CreateForm(self.request.POST,
            group=group,
            sent_by=self.request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            self.invalidform = form
            return self.get(*args, **kwargs)

    def get_success_url(self):
        return reverse('devilry_student_groupinvite_create', kwargs=self.kwargs)

    def form_valid(self, form):
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(GroupInviteCreateView, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['form'] = CreateForm()
        else:
            context['form'] = self.invalidform
        return context