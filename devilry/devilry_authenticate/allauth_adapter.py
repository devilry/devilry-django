import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from devilry.devilry_authenticate import socialaccount_user_updaters

logger = logging.getLogger(__name__)


class DevilrySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        updater = socialaccount_user_updaters.get_updater(
            provider_id=sociallogin.account.provider)
        shortname = updater.make_shortname(
            socialaccount=sociallogin.account)
        try:
            existing_user = get_user_model().objects.get(shortname=shortname)
        except get_user_model().DoesNotExist:
            sociallogin.user.shortname = shortname
        else:
            sociallogin.user = existing_user

        sociallogin.user.set_unusable_password()
        sociallogin.user.full_clean()
        sociallogin.user.save()
        sociallogin.save(request)
        return sociallogin.user

    def populate_user(self,
                      request,
                      sociallogin,
                      data):
        return sociallogin.user

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Log errors with allauth authentication.
        """
        logger.error(
            'Allauth authentication failed. Provider_id: %s. Error: %s. Extra_context: %r. Exception: %s',
            provider_id, error, extra_context, exception)
