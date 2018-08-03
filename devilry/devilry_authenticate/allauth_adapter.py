import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from devilry.devilry_authenticate import socialaccount_user_updaters

logger = logging.getLogger(__name__)


class DevilrySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # Debug log
        logger.debug(msg='DevilrySocialAccountAdapter.save_user:')

        updater = socialaccount_user_updaters.get_updater(
            provider_id=sociallogin.account.provider)

        # Debug log
        logger.debug(msg='Fetching updater (type): {}'.format(type(updater)))

        shortname = updater.make_shortname(
            socialaccount=sociallogin.account)

        # Debug log
        logger.debug(msg='Make shortname from updater: {}'.format(shortname))

        # Debug log
        logger.debug(msg='Fetch user')
        try:
            existing_user = get_user_model().objects.get(shortname=shortname)
        except get_user_model().DoesNotExist:
            # Debug log
            logger.debug(msg='User does not exist, setting sociallogin.user.shortname to {}'.format(shortname))
            sociallogin.user.shortname = shortname
        else:
            # Debug log
            logger.debug(msg='User exists, setting sociallogin.user to existing_user')
            sociallogin.user = existing_user

        sociallogin.user.set_unusable_password()
        sociallogin.user.full_clean()
        sociallogin.user.save()
        sociallogin.save(request)
        # Debug log
        logger.debug(msg='User saved')
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
