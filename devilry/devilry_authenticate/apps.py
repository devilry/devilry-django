from django.apps import AppConfig


class DataPortenUserUpdater(object):
    def __init__(self, user, socialaccount):
        self.user = user
        self.socialaccount = socialaccount

    @property
    def extra_data(self):
        return self.socialaccount.extra_data

    def get_email(self):
        email = self.extra_data.get('email', None) or ''
        if '@' not in email:
            email = ''
        return email

    def get_shortname(self):
        userid_sec = self.extra_data['userid_sec'][0]
        if userid_sec.startswith('feide:'):
            if userid_sec.endswith('uio.no'):
                return userid_sec[len('feide:'):].split('@')[0]
            else:
                return userid_sec
        else:
            return 'userid:{}'.format(self.extra_data['userid'])

    def create_useremail_if_needed(self):
        from devilry.devilry_account.models import UserEmail
        email = self.get_email()
        if not UserEmail.objects.filter(user=self.user, email=email).exists():
            useremail = UserEmail(user=self.user, email=email, is_primary=True)
            useremail.full_clean()
            useremail.save()

    def save(self):
        self.user.shortname = self.get_shortname()
        self.user.full_clean()
        self.user.save()
        self.create_useremail_if_needed()


class AuthenticateAppConfig(AppConfig):
    name = 'devilry.devilry_authenticate'
    verbose_name = "Devilry authenticate"

    def _sync_allauth_account_with_devilry_user(self, user, socialaccount):
        from allauth.socialaccount.providers.dataporten.provider import DataportenProvider
        provider = socialaccount.provider
        if provider == DataportenProvider.id:
            DataPortenUserUpdater(user=user, socialaccount=socialaccount).save()

    def _on_user_signed_up(self, request, user, **kwargs):
        from allauth.socialaccount.models import SocialAccount
        socialaccount = SocialAccount.objects.get(user=user)
        self._sync_allauth_account_with_devilry_user(
            user=user, socialaccount=socialaccount)

    def _on_social_account_updated(self, request, sociallogin, **kwargs):
        self._sync_allauth_account_with_devilry_user(
            user=sociallogin.user,
            socialaccount=sociallogin.account)

    def ready(self):
        from allauth.socialaccount import signals as socialaccount_signals
        from allauth.account import signals as account_signals
        account_signals.user_signed_up.connect(self._on_user_signed_up)
        socialaccount_signals.social_account_updated.connect(self._on_social_account_updated)
