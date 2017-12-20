from allauth.account.views import LoginView
from allauth.socialaccount import providers
from django.conf import settings
from django.http import HttpResponseRedirect


class AllauthLoginView(LoginView):
    template_name = 'devilry_authenticate/allauth/login.django.html'

    def get(self, *args, **kwargs):
        allauth_backend = 'allauth.account.auth_backends.AuthenticationBackend'
        all_providers = providers.registry.get_list(request=self.request)
        if len(settings.AUTHENTICATION_BACKENDS) == 1 \
                and allauth_backend in settings.AUTHENTICATION_BACKENDS \
                and len(all_providers) == 1:
            provider = all_providers[0]
            return HttpResponseRedirect(
                provider.get_login_url(
                    request=self.request,
                    process='login'))
        return super(AllauthLoginView, self).get(*args, **kwargs)
