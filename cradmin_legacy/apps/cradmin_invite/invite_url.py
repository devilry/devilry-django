from django.conf import settings

from cradmin_legacy.apps.cradmin_email import emailutils
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    get_expiration_datetime_for_app,
)


class InviteEmail(emailutils.AbstractEmail):
    """
    The default invite email class for :class:`.InviteUrl`.

    You may want to provide your own and override
    :meth:`.InviteUrl.get_invite_email_class`.
    """

    subject_template = "cradmin_invite/email/subject.django.txt"
    html_message_template = "cradmin_invite/email/html_message.django.html"

    def get_context_data(self):
        context = super().get_context_data()
        context.update({"CRADMIN_LEGACY_SITENAME": settings.CRADMIN_LEGACY_SITENAME})
        return context


class InviteUrl:
    """
    Sends an email with a link that the user clicks to accept an invite.

    Example:
        ::

            from cradmin_legacy.apps.cradmin_invite.utils import InviteUrl

            class InviteUrl(InviteUrl):
                def get_appname(self):
                    return 'myapp'

                def get_confirm_invite_url(self, generictoken):
                    return reverse('myapp-confirm-invite', kwargs={
                        'token': generictoken.token
                    })

            def myview(request):
                InviteUrl(request=request, private=True, content_object=someobject).send_email(
                    'test@example.com', 'test2@example.com')
                # ... or ...
                share_url = InviteUrl(request=request, private=False, content_object=someobject).get_share_url()
                # ... or ...
                InviteUrl(request=request, private=False, content_object=someobject).send_email(
                    'test@example.com', 'test2@example.com', 'test3@example.com')
    """

    def __init__(self, request, private, content_object, metadata=None, **kwargs):
        """

        Parameters:
            request: A Django HttpRequest object.
            private: If this is ``True`` we send unique single-use invite URLs.
            metadata: Metadata to accociate with the invite.

        """
        self.request = request
        self.private = private
        self.content_object = content_object
        self.metadata = metadata
        if "expiration_datetime" in kwargs:
            self.expiration_datetime = kwargs["expiration_datetime"]

    def get_appname(self):
        """
        Get the appname for
        :obj:`django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata.app`.

        You must override this in subclasses.
        """
        raise NotImplementedError()

    def get_confirm_invite_url(self, generictoken):
        """
        Get the confirm invite view URL.

        Must be implemented in subclasses.

        Parameters:
            generictoken: A
                :class:`~django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata`
                object.
        """
        raise NotImplementedError()

    def __get_absolute_confirm_invite_url(self, generictoken):
        return self.request.build_absolute_uri(self.get_confirm_invite_url(generictoken))

    def get_from_email(self):
        """
        Get the email sender address.

        Defaults to the ``CRADMIN_LEGACY_INVITE_FROM_EMAIL`` setting
        falling back on the ``DEFAULT_FROM_EMAIL`` setting.
        """
        return getattr(settings, "CRADMIN_LEGACY_INVITE_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)

    def get_expiration_datetime(self):
        """
        Get the value to use for the ``expiration_datetime`` attribute of
        :class:`~django_cradmin.apps.cradmin_generic_token_with_metadata.models.GenericTokenWithMetadata`.

        Defaults to the expiration_datetime provided via the constructor,
        and falls back to getting the configured expiration datetime for
        the app.
        """
        if hasattr(self, "expiration_datetime"):
            return self.expiration_datetime
        else:
            return get_expiration_datetime_for_app(self.get_appname())

    def _generate_generictoken(self, email=None):
        metadata = self.metadata
        if email:
            if self.metadata is None:
                metadata = {"email": email}
            elif isinstance(self.metadata, dict):
                if "email" not in self.metadata:
                    metadata = self.metadata.copy()
                    metadata["email"] = email

        return GenericTokenWithMetadata.objects.generate(
            app=self.get_appname(),
            expiration_datetime=self.get_expiration_datetime(),
            content_object=self.content_object,
            metadata=metadata,
        )

    def generate_generictoken(self, email=None):
        if self.private:
            # If private generate unique tokens
            return self._generate_generictoken(email=email)
        else:
            # If public, re-use the same token and ignore email argument
            if hasattr(self, "_generictoken"):
                return self._generictoken
            else:
                self._generictoken = self._generate_generictoken()
                return self._generictoken

    def get_invite_email_class(self):
        """
        Must return a subclass of :class:`cradmin_legacy.apps.cradmin_email.emailutils.AbstractEmail`.

        Defaults to :class:`.InviteEmail`.
        """
        return InviteEmail

    def get_extra_invite_email_context_data(self, generictoken):
        """
        Override this to provide extra context data for the
        :meth:`.get_invite_email_class`.

        Make sure you call ``super`` and extend the returned dict.
        """
        return {"confirm_invite_url": self.__get_absolute_confirm_invite_url(generictoken)}

    def send_email(self, *emails):
        """
        Generate a token and send an email containing an absolute invite
        URL for that token.

        If this InviteUrl is private, we generate a new token each
        email recipient, and if it is public, we re-use the same
        token.

        Private tokens are generated as single use tokens, and public tokens
        are unlimited use tokens.

        Private tokens gets the email automatically added to the metadata
        if metadata is a dict or None.
        """
        # TODO: Re-use email connection
        invite_email_class = self.get_invite_email_class()
        for email in emails:
            generictoken = self.generate_generictoken(email)
            invite_email_class(
                recipient=email,
                from_email=self.get_from_email(),
                extra_context_data=self.get_extra_invite_email_context_data(generictoken),
            ).send()

    def get_share_url(self):
        """
        Generate a token and return an absolute invite URL for that token.

        If this InviteUrl is private, we generate a new token each
        time this is called, and if it is public, we re-use the same
        token.

        Private tokens are generated as single use tokens, and public tokens
        are unlimited use tokens.
        """
        generictoken = self.generate_generictoken()
        return self.__get_absolute_confirm_invite_url(generictoken)

        # def get_tokens_stored_for_app(self):
        #     return GenericTokenWithMetadata.objects.filter_not_expired().filter(app=self.get_appname())
