from django.views.generic.edit import DeleteView
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite


class GroupInviteDeleteView(DeleteView):
    template_name = 'devilry_student/groupinvite_delete.django.html'
    pk_url_kwarg = 'invite_id'
    context_object_name = 'groupinvite'

    def get_queryset(self):
        return GroupInvite.objects.filter_no_response().filter(sent_by=self.request.user)

    def get_success_url(self):
        return reverse('devilry_student_projectgroup_overview', kwargs={'group_id': self.group.id})

    def post(self, *args, **kwargs):
        invite = self.get_object()
        self.group = invite.group
        return super(GroupInviteDeleteView, self).post(*args, **kwargs)
