from django.views.generic.detail import DetailView
from django import forms
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from devilry.apps.core.models import GroupInvite


class GroupInviteRespondView(DetailView):
    template_name = 'devilry_student/groupinvite_respond.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_unanswered_received_invites(self.request.user)

    def get_success_url(self):
        return reverse('devilry_student_projectgroup_overview',
            kwargs={'group_id': self.group.id})

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
            return redirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        context = super(GroupInviteRespondView, self).get_context_data(**kwargs)
        context['errormessage'] = getattr(self, 'errormessage', None)
        return context
