import json
import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


# class DevilryAccountAdapter(DefaultAccountAdapter):
#     def save_user(self, request, user, form, commit=True):
#         user = super(DevilryAccountAdapter, self).save_user(request, user, form, commit=False)
#         user.full_clean()
#         user.save()
#         return user


class DevilrySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self,
                      request,
                      sociallogin,
                      data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social user that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict
        free. For example, verifying whether or not the username
        already exists, is not a responsibility.
        """
        return sociallogin.user

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Log errors with allauth authentication.
        """
        logger.error(
            'Allauth authentication failed. Provider_id: %s. Error: %s. Extra_context: %r. Exception: %s',
            provider_id, error, extra_context, exception)
