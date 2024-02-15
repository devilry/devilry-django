import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.conf import settings

from devilry.devilry_authenticate import socialaccount_user_updaters

logger = logging.getLogger(__name__)


class MisalignedProviderResponseError(Exception):
    """
    Raised by :class:`.DevilrySocialAccountAdapter` if the response from a
    social account provider lack expected root elements and/or had surplus
    root elements when compared with `SOCIALACCOUNT_EXPECTED_RESPONSE`.
    """
    def __init__(self, msg):
        self.msg = msg


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
            connecting = False
        else:
            # Debug log
            logger.debug(msg='User exists, setting sociallogin.user to existing_user')
            sociallogin.user = existing_user
            connecting = True

        expected_response = getattr(settings, 'SOCIALACCOUNT_EXPECTED_RESPONSE', None)
        if expected_response:
            response_keys = sociallogin.account.extra_data.keys()
            if response_keys != expected_response.keys():
                try:
                    extra_keys = set(response_keys).difference(expected_response.keys())
                    if extra_keys:
                        for key in extra_keys:
                            sociallogin.account.extra_data.pop(key, None)
                        raise MisalignedProviderResponseError('{} unexpected element(s) removed from extra_data.'.format(len(extra_keys)))
                    else:
                        raise MisalignedProviderResponseError('Expected element(s) missing from response.')
                except MisalignedProviderResponseError as err:
                    try:
                        from sentry_sdk import capture_exception as sentry_capture_exception, set_user as sentry_set_user
                        if shortname:
                            sentry_set_user({"username": shortname})
                        sentry_capture_exception(err)
                    except ImportError:
                        logger.error('Misaligned provider response: %s', err.msg)

        sociallogin.user.set_unusable_password()
        sociallogin.user.full_clean()
        sociallogin.user.save()
        sociallogin.save(request, connecting)
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
