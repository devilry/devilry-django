from django.contrib.auth import get_user_model

from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django_cradmin import crapp
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django_cradmin.crinstance import reverse_cradmin_url
from django.views.generic.edit import DeleteView

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import GroupInvite


class CreateForm(forms.ModelForm):
    sent_to = forms.TypedChoiceField(
        label=ugettext_lazy('Send invitation to'),
        choices=[],
        required=True,
        coerce=int,
        help_text=ugettext_lazy('Select the student you want to invite to your group.'))

    class Meta:
        model = AssignmentGroup
        fields = ['sent_to']

    def _sent_to_choices(self):
        candidates = GroupInvite.send_invite_to_choices_queryset(self.group)
        choices = [
            (candidate.relatedstudent.user_id, candidate.relatedstudent.user.get_displayname())
            for candidate in candidates]
        choices.insert(0, ('', ''))
        return choices

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        form_action = kwargs.pop('form_action')
        self.sent_by = kwargs.pop('sent_by')
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['sent_to'].choices = self._sent_to_choices()
        self.helper = FormHelper()
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            'sent_to',
            ButtonHolder(
                Submit('submit', ugettext_lazy('Send invitation'))
            )
        )

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        sent_to_userid = cleaned_data.get('sent_to')
        if sent_to_userid:
            try:
                sent_to = GroupInvite.validate_user_id_send_to(self.group, sent_to_userid)
            except ValidationError:
                ValidationError(ugettext_lazy('Cannot invite student'))
            else:
                invite = GroupInvite(group=self.group, sent_by=self.sent_by, sent_to=sent_to)
                invite.full_clean()
                self.cleaned_invite = invite
        return cleaned_data


class ProjectGroupOverviewView(TemplateView):
    template_name = 'devilry_student/cradmin_group/projectgroupapp/projectgroup_overview.django.html'
    pk_url_kwarg = 'group_id'
    context_object_name = 'group'

    def get_queryset(self):
        return AssignmentGroup.objects.filter_student_has_access(self.request.user) \
            .select_related(
            'parentnode',  # Assignment
            'parentnode__parentnode',  # Period
            'parentnode__parentnode__parentnode')  # Subject

    def _form_kwargs(self):
        return dict(
            group=self.request.cradmin_role,
            form_action=self.request.path,
            sent_by=self.request.user)

    def post(self, *args, **kwargs):
        form = CreateForm(self.request.POST, **self._form_kwargs())
        if form.is_valid():
            return self.form_valid(form)
        else:
            self.invalidform = form
            return self.get(*args, **kwargs)

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.cleaned_invite.save()
        form.cleaned_invite.send_invite_notification(self.request)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ProjectGroupOverviewView, self).get_context_data(**kwargs)
        group = self.request.cradmin_role
        context['group'] = group
        if self.request.method == 'GET':
            context['form'] = CreateForm(**self._form_kwargs())
        else:
            context['form'] = self.invalidform
        context['unanswered_received_invites'] = GroupInvite.objects \
            .filter_unanswered_received_invites(self.request.user) \
            .filter(group__parentnode=group.parentnode)
        context['unanswered_sent_invites'] = GroupInvite.objects.filter_unanswered_sent_invites(group)

        context['groupmemberusers'] = list(
            get_user_model().objects
            .filter(id__in=group.candidates.values_list('relatedstudent__user_id', flat=True))
            .prefetch_related_primary_email()
            .prefetch_related_primary_username())
        return context


class GroupInviteRespondView(DetailView):
    template_name = 'devilry_student/cradmin_group/projectgroupapp/groupinvite_respond.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_unanswered_received_invites(self.request.user)

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME)

    def get_declined_or_error_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def post(self, *args, **kwargs):
        invite = self.get_object()
        self.group = invite.group

        accepted = 'accept_invite' in self.request.POST
        try:
            invite.respond(accepted=accepted)
        except ValidationError as e:
            messages.warning(
                self.request,
                ugettext_lazy(str(e))
            )
        else:
            if accepted:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Joined the group by invitation from %(student)s' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
                return redirect(self.get_success_url())
            else:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Declined group invitation from %(student)s' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
        return redirect(self.get_declined_or_error_url())

    def get_context_data(self, **kwargs):
        context = super(GroupInviteRespondView, self).get_context_data(**kwargs)
        return context


class GroupInviteDeleteView(DeleteView):
    template_name = 'devilry_student/cradmin_group/projectgroupapp/groupinvite_delete.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_no_response().filter(sent_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(GroupInviteDeleteView, self).get_context_data(**kwargs)
        context['cancel_url'] = self.request.cradmin_app.reverse_appindexurl()
        return context

    def get_success_url(self):
        messages.success(
            self.request,
            ugettext_lazy('Removed project group invitation %(student)s.' % {
                'student': self.get_object().sent_to.get_displayname()
            })
        )
        return self.request.cradmin_app.reverse_appindexurl()

    def post(self, *args, **kwargs):
        invite = self.get_object()
        self.group = invite.group
        return super(GroupInviteDeleteView, self).post(*args, **kwargs)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ProjectGroupOverviewView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^remove/(?P<invite_id>\d+)$',
            GroupInviteDeleteView.as_view(),
            name='delete'),
        crapp.Url(
            r'respond/(?P<invite_id>\d+)$',
            GroupInviteRespondView.as_view(),
            name='respond'
        )
    ]
