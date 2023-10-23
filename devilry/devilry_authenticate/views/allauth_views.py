from allauth.account.views import LoginView, LogoutView
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.dataporten.provider import DataportenProvider
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect


class AllauthLoginView(LoginView):
    template_name = 'devilry_authenticate/allauth/login.django.html'

    def _get_cradmin_auth_url(self):
        next_param = self.request.GET.get('next', None)
        url = reverse('cradmin-authenticate-login')
        if next_param:
            url += '?next=%s' % next_param

        return url

    def get(self, *args, **kwargs):
        allauth_backend = 'allauth.account.auth_backends.AuthenticationBackend'
        adapter = get_adapter(self.request)
        all_providers = adapter.list_providers(self.request)
        if len(all_providers) == 0:
            return HttpResponseRedirect(self._get_cradmin_auth_url())

        if len(settings.AUTHENTICATION_BACKENDS) == 1:
            if allauth_backend in settings.AUTHENTICATION_BACKENDS \
                    and len(all_providers) == 1:
                provider = all_providers[0]
                return HttpResponseRedirect(
                    provider.get_login_url(
                        request=self.request,
                        process='login'))
            else:
                return HttpResponseRedirect(self._get_cradmin_auth_url())
        return super(AllauthLoginView, self).get(*args, **kwargs)


class AllauthLogoutView(LogoutView):
    template_name = 'devilry_authenticate/allauth/logout.django.html'

    def dispatch(self, request, *args, **kwargs):
        # The session is deleted when get_redirect_url is called, so we need to get the provider here.
        self.allauth_provider = request.session.get('allauth_provider')
        return super(AllauthLogoutView, self).dispatch(request=request, *args, **kwargs)

    def get_redirect_url(self):
        if self.allauth_provider == DataportenProvider.id:
            return settings.DATAPORTEN_LOGOUT_URL

        #: TODO: Remove this after a while.
        #: Workaround to make sure users are logged out of Dataporten without having to log in, log out, log in and the logout
        #: again.
        if settings.AUTHENTICATION_BACKENDS == ['allauth.account.auth_backends.AuthenticationBackend',]:
            if SocialApp.objects.count() == 1:
                if SocialApp.objects.first().provider == DataportenProvider.id:
                    return settings.DATAPORTEN_LOGOUT_URL
        return super(AllauthLogoutView, self).get_redirect_url()
