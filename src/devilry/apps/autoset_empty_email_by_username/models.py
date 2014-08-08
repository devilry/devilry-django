from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings


def set_email_by_username(sender, **kwargs):
    """
    Signal handler which is invoked when a User is saved.
    """
    user = kwargs['instance']
    if not user.email:
        user.email = '{0}@{1}'.format(user.username, settings.DEVILRY_DEFAULT_EMAIL_SUFFIX)

post_save.connect(set_email_by_username,
                  sender=User)
