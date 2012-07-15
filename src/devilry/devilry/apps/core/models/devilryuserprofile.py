from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


def user_is_admin(userobj):
    """
    Check if the given user is admin on any node, subject, period or
    assignment.
    """
    from .node import Node
    from .subject import Subject
    from .period import Period
    from .assignment import Assignment
    for cls in (Node, Subject, Period, Assignment):
        if cls.where_is_admin(userobj).count() > 0:
            return True
    return False

def user_is_admin_or_superadmin(userobj):
    """
    Return ``True`` if ``userobj.is_superuser``, and fall back to calling
    :func:`.user_is_admin` if not.
    """
    if userobj.is_superuser:
        return True
    else:
        return user_is_admin(userobj)


class DevilryUserProfile(models.Model):
    """ User profile with a one-to-one relation to ``django.contrib.auth.models.User``.

    Ment to be used as a Django *user profile* (AUTH_PROFILE_MODULE).

    .. attribute:: full_name

        Django splits names into first_name and last_name. They are only 30 chars each.
        Read about why this is not a good idea here:

            http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/

        Since we require support for *any* name, we use our own ``full_name``
        field, and ignore the one in Django. Max length 300.

    .. attribute:: languagecode

        Used to store the preferred language for a user.
    """
    user = models.OneToOneField(User) # This field is required, and it must be named ``user`` (because the model is used as a AUTH_PROFILE_MODULE)
    full_name = models.CharField(max_length=300, blank=True, null=True)
    languagecode = models.CharField(max_length=100)

    class Meta:
        app_label = 'core'


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        DevilryUserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
