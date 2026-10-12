from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.translation import gettext_lazy

from django.shortcuts import render
from django.utils.http import urlencode
from django.views.generic import TemplateView

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    GenericTokenExpiredError,
)


class AbstractAcceptInviteView(TemplateView):
    """
    Base class for views that accept invites from
    :class:`~cradmin_legacy.apps.cradmin_invite.invite_url.InviteUrl`.

    You have to override:

    - :meth:`~.AbstractAcceptInviteView.get_appname`.
    - :meth:`~.AbstractAcceptInviteView.invite_accepted`.
    """

    template_name = "cradmin_invite/accept/accept.django.html"

    #: Default value for :meth:`~.AbstractAcceptInviteView.get_description_template_name`.
    description_template_name = "cradmin_invite/accept/description.django.html"

    #: Default value for :meth:`~.AbstractAcceptInviteView.get_token_error_template_name`.
    token_error_template_name = "cradmin_invite/accept/token_error.django.html"

    def get_pagetitle(self):
        """
        Get the title of the page.
        """
        return gettext_lazy("Accept invite")

    def get_accept_as_button_label(self):
        """
        Get the label of the *Accept as authenticated user* button.
        """
        return gettext_lazy("Accept as %(user)s") % {"user": self.request.user}

    def get_register_account_button_label(self):
        """
        Get the label of the *Sign up* button.
        """
        return gettext_lazy("Sign up for %(sitename)s") % {"sitename": settings.CRADMIN_LEGACY_SITENAME}

    def get_login_as_different_user_button_label(self):
        """
        Get the label of the *Sign in as different user* button.
        """
        return gettext_lazy("Sign in as another user")

    def get_login_button_label(self):
        """
        Get the label of the *Sign in* button.
        """
        return gettext_lazy("Sign in")

    def get_description_template_name(self):
        """
        The template used to render the description of the invite.
        The template context is the one returned by :meth:`~AbstractAcceptInviteView.get_context_data`.

        Defaults to :obj:`.description_template_name`.
        """
        return self.description_template_name

    def get_token_error_template_name(self):
        """
        The template used to render the view when the given token does not
        validate. If you just want to change the error messages, you can extend
        the ``cradmin_invite/accept/token_error.django.html`` template and override
        the ``invalid_token_message`` and ``expired_token_message`` blocks.

        Defaults to :obj:`.token_error_template_name`.
        """
        return self.token_error_template_name

    def dispatch(self, request, *args, **kwargs):
        """
        Takes care of validating the token for both GET and POST
        requests.

        If the token is valid, we set ``self.generic_token`` to the
        :class:`~django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata`.

        If the token is invalid, we respond with :meth:`.token_error_response`.
        """
        try:
            generictoken = GenericTokenWithMetadata.objects.get_and_validate(
                token=self.kwargs["token"], app=self.get_appname()
            )
        except GenericTokenWithMetadata.DoesNotExist:
            return self.token_error_response(token_does_not_exist=True)
        except GenericTokenExpiredError:
            return self.token_error_response(token_expired=True)
        else:
            self.generictoken = generictoken
            return super().dispatch(request, *args, **kwargs)

    def token_error_response(self, token_does_not_exist=False, token_expired=False):
        """
        Generates the response when the token does not validate.

        Unless you have some special needs, you will most likely want to just override
        :obj:`.token_error_template_name` instead of this view.
        """
        return render(
            self.request,
            self.get_token_error_template_name(),
            {"token_does_not_exist": token_does_not_exist, "token_expired": token_expired},
        )

    def add_next_argument_to_url(self, url, next_url=None):
        """
        Adds ``?next=<next_url>`` to the given ``url``.

        Parameters:
            url: The base url.
            next_url: The url to redirect to after whatever ``url`` does is successfully completed.
                Defaults to the absolute URI of the current request.
        """
        if not next_url:
            next_url = self.request.build_absolute_uri()
        return "{url}?{arguments}".format(url=url, arguments=urlencode({"next": next_url}))

    def get_register_account_url(self):
        """
        Get the URL to used to create a new user.

        Should have some way of returning the user to this view after
        the user has been created.

        Defaults to the ``cradmin-register-account-begin`` view in
        ``cradmin_legacy.apps.cradmin_register_account``.
        """
        return self.add_next_argument_to_url(reverse("cradmin-register-account-begin"))

    def get_login_url(self):
        """
        Get the URL to used to login if not already authenticated.

        Should have some way of returning the user to this view after
        login is complete.

        Defaults to ``settings.LOGIN_URL``.
        """
        return self.add_next_argument_to_url(settings.LOGIN_URL)

    def get_login_as_different_user_url(self):
        """
        Get the URL to used to login as a different user.

        Should have some way of returning the user to this view after
        login is complete.

        Defaults to the ``cradmin-authenticate-logout`` view in ``cradmin_legacy.apps.cradmin_authenticate``
        with the next-argument set to the ``cradmin-authenticate-login`` view in the same app, with the next
        argument of the ``cradmin-authenticate-login`` view set to the current url.
        """
        return self.add_next_argument_to_url(url=reverse("cradmin-authenticate-logout"), next_url=self.get_login_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pagetitle"] = self.get_pagetitle()
        context["description_template_name"] = self.get_description_template_name()

        context["register_account_url"] = self.get_register_account_url()
        context["login_url"] = self.get_login_url()
        context["login_as_different_user_url"] = self.get_login_as_different_user_url()

        context["accept_as_button_label"] = self.get_accept_as_button_label()
        context["register_account_button_label"] = self.get_register_account_button_label()
        context["login_as_different_user_button_label"] = self.get_login_as_different_user_button_label()
        context["login_button_label"] = self.get_login_button_label()
        return context

    def post(self, *args, **kwargs):
        """
        If the user is authenticated, we return :meth:`~.AbstractAcceptInviteView.invite_accepted`.
        If the user is not authenticated, we raise :exc:`django.core.exceptions.PermissionDenied`.
        """
        if self.request.user.is_authenticated:
            return self.invite_accepted(self.generictoken)
        else:
            raise PermissionDenied()

    def get_appname(self):
        """
        Get the name of the appname. Must match the appname returned by the
        :class:`~cradmin_legacy.apps.cradmin_invite.invite_url.InviteUrl.get_appname`
        method of your :class:`~cradmin_legacy.apps.cradmin_invite.invite_url.InviteUrl`
        subclass.
        """
        raise NotImplementedError()

    def invite_accepted(self, token):
        """
        Called on POST when the invite has been accepted
        by the user.

        At this point, ``self.request.user`` is the user accepting the invite.
        """
        raise NotImplementedError()
