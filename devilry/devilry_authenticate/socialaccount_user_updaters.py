from devilry.devilry_dataporten_allauth.provider import DevilryDataportenProvider
from django.conf import settings


class AbstractUserUpdater(object):
    def __init__(self, user, socialaccount):
        self.user = user
        self.socialaccount = socialaccount

    @property
    def extra_data(self):
        return self.socialaccount.extra_data

    def create_useremail_if_needed(self):
        from devilry.devilry_account.models import UserEmail
        email = self.get_email()
        if not UserEmail.objects.filter(user=self.user, email=email).exists():
            useremail = UserEmail(user=self.user, email=email, is_primary=True)
            useremail.full_clean()
            useremail.save()

    def get_shortname(self):
        return self.__class__.make_shortname(socialaccount=self.socialaccount)

    def update_user(self):
        self.user.shortname = self.get_shortname()
        self.user.fullname = self.get_fullname()
        self.user.full_clean()
        self.user.save()
        self.create_useremail_if_needed()

    @classmethod
    def make_shortname(cls, socialaccount):
        raise NotImplementedError()

    def get_email(self):
        raise NotImplementedError()

    def get_fullname(self):
        raise NotImplementedError()


class DataPortenUserUpdater(AbstractUserUpdater):
    @classmethod
    def make_shortname(cls, socialaccount):
        extra_data = socialaccount.extra_data
        userid_sec = extra_data['userid_sec'][0]
        if userid_sec.startswith('feide:'):
            feide_userid_sec_to_username_suffix = getattr(
                settings, 'DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX', None)
            if feide_userid_sec_to_username_suffix \
                    and userid_sec.endswith(feide_userid_sec_to_username_suffix):
                return userid_sec[len('feide:'):].split('@')[0]
            else:
                return userid_sec
        else:
            return 'userid:{}'.format(extra_data['userid'])

    def get_email(self):
        email = self.extra_data.get('email', '') or ''
        if '@' not in email:
            email = ''
        return email

    def get_fullname(self):
        return self.extra_data.get('name', '') or ''


socialaccount_updaters = {
    DevilryDataportenProvider.id: DataPortenUserUpdater
}


def get_updater(provider_id):
    return socialaccount_updaters.get(provider_id, None)
