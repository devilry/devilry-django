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
        for socialaccount in SocialAccount.objects.filter(user=user):
            logger.warning('No SocialAccount found for')
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
        self._sync_allauth_account_with_devilry_user(user=user)

    def _on_user_logged_in(self, request, user, **kwargs):
        self._sync_allauth_account_with_devilry_user(user=user)

    def ready(self):
        from allauth.account import signals as account_signals
        account_signals.user_signed_up.connect(self._on_user_signed_up)
        account_signals.user_logged_in.connect(self._on_user_logged_in)
