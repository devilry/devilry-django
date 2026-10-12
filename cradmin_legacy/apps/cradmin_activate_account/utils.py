from django.conf import settings

from django.urls import reverse

from cradmin_legacy.apps.cradmin_email import emailutils
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    get_expiration_datetime_for_app,
)


class ActivationEmail(emailutils.AbstractEmail):
    """
    Handles account activation. Sends an email with a link that
    the user clicks to activate their account.

    Example::

        from cradmin_legacy.apps.cradmin_activate_account.utils import ActivationEmail

        def myview(request):
            someuser = get_some_user()  # Insert your code to determine the user to activate here
            ActivationEmail(request=request, user=someuser).send()
    """

    subject_template = "cradmin_activate_account/email/subject.django.txt"
    html_message_template = "cradmin_activate_account/email/html_message.django.html"

    #: The name of the app. Used for
    #: :obj:`django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata.app`.
    #: If you override this, you also have to override :meth:`~.ActivationEmail.get_activate_url`
    #: and return the URL to a view that pops a GenericTokenWithMetadata with the
    #: changed appname.
    appname = "cradmin_activate_account"

    def __init__(self, request, user, next_url=None):
        """
        Parameters:
            request: A Django HttpRequest object.
            user: The user you want to activate. Must have an ``email`` attribute or property.
            next_url: An optional URL to redirect to after the user has activated their account.
        """
        self.user = user
        self.request = request
        self.next_url = next_url or getattr(
            settings, "CRADMIN_LEGACY_ACTIVATE_ACCOUNT_DEFAULT_NEXT_URL", settings.LOGIN_URL
        )
        self.token = self.generate_token()
        super().__init__(recipient=self.user.email)

    def get_activate_url(self, token):
        """
        Get the activate account view URL.
        """
        return reverse("cradmin-activate-account-activate", kwargs={"token": token.token})

    def get_context_data(self):
        """
        Get the context data of the email templates.
        """
        context = super().get_context_data()
        context.update(
            {"user": self.user, "activate_url": self.request.build_absolute_uri(self.get_activate_url(self.token))}
        )
        return context

    def get_from_email(self):
        """
        Get the email sender address.

        Defaults to the ``CRADMIN_LEGACY_ACTIVATE_ACCOUNT_FROM_EMAIL`` setting
        falling back on the ``DEFAULT_FROM_EMAIL`` setting.
        """
        return getattr(settings, "CRADMIN_LEGACY_ACTIVATE_ACCOUNT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)

    def get_expiration_datetime(self):
        """
        Get the value to use for the ``expiration_datetime`` attribute of
        :class:`~django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata`.
        """
        return get_expiration_datetime_for_app(self.appname)

    def generate_token(self):
        return GenericTokenWithMetadata.objects.generate(
            content_object=self.user,
            app=self.appname,
            expiration_datetime=self.get_expiration_datetime(),
            metadata={"next_url": self.next_url},
        )
