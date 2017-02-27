from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django.utils.timezone import datetime
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

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
            (candidate.id, candidate.relatedstudent.user.get_displayname())
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
        sent_to_candidate_id = cleaned_data.get('sent_to')
        if sent_to_candidate_id:
            try:
                sent_to = GroupInvite.validate_candidate_id_sent_to(self.group, sent_to_candidate_id)
            except ValidationError as e:
                self.cleaned_invite = None
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
        return self.request.cradmin_app.reverse_appindexurl()

    def form_valid(self, form):
        if form.cleaned_invite:
            form.cleaned_invite.save()
            form.cleaned_invite.send_invite_notification(self.request)
            messages.success(
                self.request,
                ugettext_lazy('Invite sent to %(student)s.' % {
                    'student': form.cleaned_invite.sent_to.get_displayname()
                })
            )
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
            .filter_allowed_to_create_groups() \
            .filter(group__parentnode=group.parentnode)
        context['unanswered_sent_invites'] = GroupInvite.objects.filter_unanswered_sent_invites(group)

        context['groupmemberusers'] = [
            user.get_displayname() for user in
            get_user_model().objects.filter(id__in=group.candidates.values_list('relatedstudent__user', flat=True))
        ]
        return context


class GroupInviteRespondView(DetailView):
    template_name = 'devilry_student/cradmin_group/projectgroupapp/groupinvite_respond.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_unanswered_received_invites(self.request.user)\
            .select_related('group__parentnode__parentnode__parentnode', 'group__cached_data')

    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME)

    def get_declined_or_error_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_context_data(self, **kwargs):
        context = super(GroupInviteRespondView, self).get_context_data(**kwargs)
        context['errormessage'] = getattr(self, 'errormessage', None)
        return context

    def get(self, request, *args, **kwargs):
        group = self.request.cradmin_role
        if group.cached_data.candidate_count > 1:
            self.errormessage = 'You are already part of a group with more than one student!'
        return super(GroupInviteRespondView, self).get(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        invite = self.get_object()
        self.group = invite.group

        accepted = 'accept_invite' in self.request.POST
        try:
            invite.respond(accepted=accepted)
        except ValidationError as e:
            messages.warning(
                self.request,
                e.messages[0]
            )
        else:
            if accepted:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Joined the group by invitation from %(student)s.' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
                return redirect(self.get_success_url())
            else:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Declined group invitation from %(student)s.' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
        return redirect(self.get_declined_or_error_url())


class GroupInviteRespondViewStandalone(DetailView):
    """
    This view is standalone and used for accepting invites through email.
    If a user has already accepted or declined an error message will be shown.
    Also if the user is already part of a group with more than 1 students an error message will be shown.
    """
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'
    template_name = 'devilry_student/cradmin_group/projectgroupapp/groupinvite_respond_standalone.django.html'

    def dispatch(self, request, *args, **kwargs):
        return super(GroupInviteRespondViewStandalone, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        We have to get all the invitations even if it already has been accepted or declined,
        since we don't want to raise 404
        Returns:
            :class:`core.GroupInvite`
        """
        return GroupInvite.objects.filter(sent_to=self.request.user)\
            .select_related('group__parentnode__parentnode__parentnode', 'group__cached_data')

    def get_success_url(self):
        """
        When a user accepts the invitation the user will be routed to the "new" feedbackfeed
        Returns:
            Url to the new group
        """
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME)

    def decline_url(self):
        """
        When a user declines the invitation the user will be routed to the "old" feedbackfeed
        Returns:
            Url to the same old group
        """
        group = AssignmentGroup.objects\
            .filter_student_has_access(self.request.user)\
            .filter(parentnode=self.group.parentnode)\
            .first()
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=group.id,
            viewname=crapp.INDEXVIEW_NAME)

    def get_current_group(self, invite):
        """
        Returns the current assignment group for the Request user
        Args:
            invite:
                :class:`core.GroupInvite`
        Returns:
            :class:`core.AssignmentGroup` The current assignment group for the Request user
        """
        return AssignmentGroup.objects.filter_student_has_access(self.request.user)\
            .filter(parentnode=invite.group.parentnode)\
            .select_related('cached_data', 'parentnode').get()

    def validate(self, invite):
        """
        checks if the user is already part of a group with more than 1 student,
        if the invite already has beed accepted or declined,
        if the students can create groups on the assignment or it has expired.
        Args:
            invite:
                :class:`core.GroupInvite`
        Raises:
            ValidationError
        """
        group = self.get_current_group(invite)
        if group.cached_data.candidate_count > 1:
            raise ValidationError(ugettext_lazy('You are already part of a group with more than one student!'))
        if invite.accepted:
            raise ValidationError(ugettext_lazy('You have already accepted this invite'))
        if invite.accepted is not None and not invite.accepted:
            raise ValidationError(ugettext_lazy('You have already declined this invite'))
        if invite.group.assignment.students_can_create_groups:
            if invite.group.assignment.students_can_not_create_groups_after and \
                            invite.group.assignment.students_can_not_create_groups_after < datetime.now():
                raise ValidationError(ugettext_lazy(
                    'Creating project groups without administrator approval is not '
                    'allowed on this assignment anymore. Please contact you course '
                    'administrator if you think this is wrong.'))
        else:
            raise ValidationError(
                ugettext_lazy('This assignment does not allow students to form project groups on their own.'))

    def get_context_data(self, **kwargs):
        context = super(GroupInviteRespondViewStandalone, self).get_context_data(**kwargs)
        context['errormessage'] = getattr(self, 'errormessage', None)
        context['exists'] = getattr(self, 'exists', True)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.validate(self.object)
        except ValidationError as e:
            self.errormessage = ' '.join(e.messages)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        invite = self.get_object()
        self.group = invite.group

        accepted = 'accept_invite' in self.request.POST
        try:
            invite.respond(accepted=accepted)
        except ValidationError as e:
            self.errormessage = ' '.join(e.messages)
            return self.get(*args, **kwargs)
        else:
            if accepted:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Joined the group by invitation from %(student)s.' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
                return redirect(self.get_success_url())
            else:
                messages.success(
                    self.request,
                    ugettext_lazy(
                        'Declined group invitation from %(student)s.' % {
                            'student': invite.sent_by.get_displayname()
                        })
                )
            return redirect(self.decline_url())


class GroupInviteDeleteView(DeleteView):
    template_name = 'devilry_student/cradmin_group/projectgroupapp/groupinvite_delete.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_no_response()\
            .filter(group__in=AssignmentGroup.objects.filter_student_has_access(self.request.user))\
            .select_related('group__parentnode__parentnode__parentnode')

    def get_context_data(self, **kwargs):
        context = super(GroupInviteDeleteView, self).get_context_data(**kwargs)
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
