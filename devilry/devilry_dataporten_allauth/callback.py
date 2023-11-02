

from allauth.socialaccount.providers.oauth2.views import OAuth2View
from requests import RequestException

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect

from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base import ProviderException, AuthError
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Error,
)
from allauth.utils import get_request_param


class DevilryOAuth2CallbackView(OAuth2View):
    """
    Subclassed to mitigate the issue where a user logged in through dataporten and used the browser back-button,
    the user was redirected to a default error view.
    """
    def dispatch(self, request, *args, **kwargs):
        if 'error' in request.GET or 'code' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                error=error)
        app = self.adapter.get_provider().app
        client = self.get_client(request, app)
        try:
            access_token = client.get_access_token(request.GET['code'])
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            if self.adapter.supports_state:
                login.state = SocialLogin \
                    .verify_and_unstash_state(
                        request,
                        get_request_param(request, 'state'))
            else:
                login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except (PermissionDenied,
                OAuth2Error,
                RequestException,
                ProviderException) as e:
            if isinstance(e, PermissionDenied) or isinstance(e, OAuth2Error):
                # One of these errors are raised when a user authenticated through dataporten
                # uses the browser back button. Simply redirect to ``/``.
                return HttpResponseRedirect('/')
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)