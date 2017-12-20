from allauth.socialaccount.providers.dataporten.provider import DataportenProvider


class AbstractUserUpdater(object):
    def __init__(self, user, socialaccount):
        self.user = user
        self.socialaccount = socialaccount

    @classmethod
    def make_shortname(cls, socialaccount):
        raise NotImplementedError()

    def get_shortname(self):
        return self.__class__.make_shortname(socialaccount=self.socialaccount)

    @property
    def extra_data(self):
        return self.socialaccount.extra_data

    def update_user(self):
        raise NotImplementedError()


class DataPortenUserUpdater(AbstractUserUpdater):
    @classmethod
    def make_shortname(cls, socialaccount):
        extra_data = socialaccount.extra_data
        userid_sec = extra_data['userid_sec'][0]
        if userid_sec.startswith('feide:'):
            if userid_sec.endswith('uio.no'):
                return userid_sec[len('feide:'):].split('@')[0]
            else:
                return userid_sec
        else:
            return 'userid:{}'.format(extra_data['userid'])

    def get_email(self):
        email = self.extra_data.get('email', None) or ''
        if '@' not in email:
            email = ''
        return email

    def create_useremail_if_needed(self):
        from devilry.devilry_account.models import UserEmail
        email = self.get_email()
        if not UserEmail.objects.filter(user=self.user, email=email).exists():
            useremail = UserEmail(user=self.user, email=email, is_primary=True)
            useremail.full_clean()
            useremail.save()

    def update_user(self):
        self.user.shortname = self.get_shortname()
        self.user.full_clean()
        self.user.save()
        self.create_useremail_if_needed()


socialaccount_updaters = {
    DataportenProvider.id: DataPortenUserUpdater
}


def get_updater(provider_id):
    return socialaccount_updaters.get(provider_id, None)
