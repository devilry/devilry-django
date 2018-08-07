import logging

from django.apps import AppConfig


logger = logging.getLogger(__name__)


class AuthenticateAppConfig(AppConfig):
    name = 'devilry.devilry_authenticate'
    verbose_name = "Devilry authenticate"

    def _sync_allauth_account_with_devilry_user(self, user):
        from devilry.devilry_authenticate import socialaccount_user_updaters
        from allauth.socialaccount.models import SocialAccount
        found_supported_socialaccount = False
        logger.debug('user: {}'.format(user))
        logger.debug('Iterating through SocialAccounts for user({}):'.format(user))
        for socialaccount in SocialAccount.objects.filter(user=user):
            logger.debug('SocialAccount.id: {}'.format(socialaccount.id))
            logger.debug('SocialAccount.user: {}'.format(socialaccount.user))
            logger.debug('SocialAccount.user.id: {}'.format(socialaccount.user.id))
            logger.debug('SocialAccount.user.shortname: {}'.format(socialaccount.user.shortname))
            logger.debug('...')
            provider_id = socialaccount.provider
            updater = socialaccount_user_updaters.get_updater(provider_id=provider_id)
            if updater:
                updater(user=user, socialaccount=socialaccount).update_user()
                found_supported_socialaccount = True
            else:
                logger.warning('No user updater found for allauth provider %r', provider_id)
        if not found_supported_socialaccount:
            logger.warning('No SocialAccount object found for user #%d', user.id)

    def _on_user_signed_up(self, request, user, **kwargs):
        logger.debug('_on_user_signed_up')
        logger.debug('user#{}'.format(user.id))
        self._sync_allauth_account_with_devilry_user(user=user)

    def _on_user_logged_in(self, request, user, **kwargs):
        logger.debug('_on_user_logged_in')
        logger.debug('user#{}'.format(user.id))
        self._sync_allauth_account_with_devilry_user(user=user)

    def _pre_social_login(self, request, sociallogin, **kwargs):
        logger.debug('_pre_social_login')
        request.session['allauth_provider'] = sociallogin.account.provider

    def ready(self):
        from allauth.account import signals as account_signals
        from allauth.socialaccount import signals as socialaccount_signals
        account_signals.user_signed_up.connect(self._on_user_signed_up)
        account_signals.user_logged_in.connect(self._on_user_logged_in)
        socialaccount_signals.pre_social_login.connect(self._pre_social_login)
