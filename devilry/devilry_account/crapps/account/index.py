from __future__ import unicode_literals

from django.conf import settings
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'devilry_account/crapps/account/index.django.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['email_auth_backend'] = settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND
        context['useremails'] = list(self.request.user.useremail_set.all())
        context['useremail_count'] = len(context['useremails'])
        context['usernames'] = list(self.request.user.username_set.all())
        context['username_count'] = len(context['usernames'])
        return context
