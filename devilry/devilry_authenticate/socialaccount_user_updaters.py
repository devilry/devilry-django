import logging

from devilry.devilry_dataporten_allauth.provider import DevilryDataportenProvider
from django.conf import settings

logger = logging.getLogger(__name__)


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

        # Debug log
        logger.debug(msg='{}.update_user'.format(type(self)))

        self.user.shortname = self.get_shortname()

        # Debug log
        logger.debug(msg='self.user.shortname set to {}'.format(self.user.shortname))
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
        # Debug log
        logger.debug(msg='{}.make_shortname:'.format(type(cls)))

        # Debug log
        logger.debug(msg='socialaccount.extra_data: {}'.format(socialaccount.extra_data))

        extra_data = socialaccount.extra_data
        userid_sec = extra_data['userid_sec'][0]
        if userid_sec.startswith('feide:'):

            # Debug log
            logger.debug(msg='userid_sec starts with feide:')

            feide_userid_sec_to_username_suffix = getattr(
                settings, 'DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX', None)

            # Debug log
            logger.debug(msg='DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX: {}'.format(
                feide_userid_sec_to_username_suffix))

            if feide_userid_sec_to_username_suffix \
                    and userid_sec.endswith(feide_userid_sec_to_username_suffix):

                # Debug log
                logger.debug(msg='feide_userid_sec_to_username_suffix is not None, and userid_sec ends with {}'.format(
                    feide_userid_sec_to_username_suffix))

                return userid_sec[len('feide:'):].split('@')[0]
            else:
                # Debug log
                logger.debug(msg='feide_userid_sec_to_username_suffix is None, or userid_sec does not end with {}'.format(
                    feide_userid_sec_to_username_suffix))
                return userid_sec
        else:
            # Debug log
            logger.debug(msg='userid_sec does NOT start with feide:')

            # Debug log
            logger.debug(msg='Returns: {}'.format('userid:{}'.format(extra_data['userid'])))

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
