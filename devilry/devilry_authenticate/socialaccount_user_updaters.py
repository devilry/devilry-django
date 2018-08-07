import logging

from django.contrib.auth import get_user_model

from devilry.devilry_dataporten_allauth.provider import DevilryDataportenProvider
from django.conf import settings

logger = logging.getLogger(__name__)


class AbstractUserUpdater(object):
    def __init__(self, user, socialaccount):
        logger.debug('User: {}#{}, Social account user: {}'.format(user, user.id, socialaccount.user))
        self.user = user
        self.socialaccount = socialaccount

    @property
    def extra_data(self):
        return self.socialaccount.extra_data

    def create_useremail_if_needed(self):
        from devilry.devilry_account.models import UserEmail
        email = self.get_email()

        # Debug log
        logger.debug('Method: create_useremail_if_needed()')
        logger.debug('{}: {}'.format(self.user.shortname, self.user.id))
        logger.debug('{}'.format(email))
        logger.debug('UserEmail for {}:'.format(self.user))

        if not email:
            email = '{}{}'.format(self.user.shortname, settings.DEVILRY_DEFAULT_EMAIL_SUFFIX)

            # Debug log
            logger.debug('No email provided by dataporten - using {!r}'.format(email))

        # Debug log
        for useremail in UserEmail.objects.filter(email=email):
            logger.debug('{}'.format(useremail))

        if not UserEmail.objects.filter(user=self.user, email=email).exists():
            useremail = UserEmail(user=self.user, email=email, is_primary=True)

            # Debug log
            logger.debug('UserEmail DOES NOT EXIST FOR USER')

            useremail.full_clean()
            useremail.save()

        # Debug log
        logger.debug('All user emails for {}'.format(self.user))

        for user_email in UserEmail.objects.filter(user_id=self.user.id):
            logger.debug('{}'.format(user_email))
        logger.debug('...')

    def get_shortname(self):
        return self.__class__.make_shortname(socialaccount=self.socialaccount)

    def update_user(self):
        logger.debug('social account user ID: {}'.format(self.socialaccount.user.id))
        logger.debug('user ID to update: {}'.format(self.user.id))

        # Debug log
        logger.debug('{}.update_user'.format(type(self)))

        self.user.shortname = self.get_shortname()

        # Debug log
        logger.debug('self.user.shortname set to {}'.format(self.user.shortname))
        logger.debug('...')

        self.user.fullname = self.get_fullname()
        self.user.full_clean()
        self.user.save()
        self.create_useremail_if_needed()

        # Debug log
        logger.debug('...')

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
        logger.debug('{}.make_shortname:'.format(type(cls)))

        # Debug log
        logger.debug('socialaccount.extra_data: {}'.format(socialaccount.extra_data))

        extra_data = socialaccount.extra_data
        userid_sec = extra_data['userid_sec'][0]
        if userid_sec.startswith('feide:'):

            # Debug log
            logger.debug('userid_sec starts with feide:')

            feide_userid_sec_to_username_suffix = getattr(
                settings, 'DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX', None)

            # Debug log
            logger.debug('DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX: {}'.format(
                feide_userid_sec_to_username_suffix))

            if feide_userid_sec_to_username_suffix \
                    and userid_sec.endswith(feide_userid_sec_to_username_suffix):

                # Debug log
                logger.debug('feide_userid_sec_to_username_suffix is not None, and userid_sec ends with {}'.format(
                    feide_userid_sec_to_username_suffix))
                logger.debug('...')
                return userid_sec[len('feide:'):].split('@')[0]
            else:
                # Debug log
                logger.debug('feide_userid_sec_to_username_suffix is None, or userid_sec does not end with {}'.format(
                    feide_userid_sec_to_username_suffix))
                logger.debug('...')
                return userid_sec
        else:
            # Debug log
            logger.debug('userid_sec does NOT start with feide:')

            # Debug log
            logger.debug('Returns: {}'.format('userid:{}'.format(extra_data['userid'])))
            logger.debug('...')
            return 'userid:{}'.format(extra_data['userid'])

    def get_email(self):
        email = self.extra_data.get('email', '') or ''
        if '@' not in email:
            email = ''
        return email.strip()

    def get_fullname(self):
        return self.extra_data.get('name', '') or ''


socialaccount_updaters = {
    DevilryDataportenProvider.id: DataPortenUserUpdater
}


def get_updater(provider_id):
    return socialaccount_updaters.get(provider_id, None)
