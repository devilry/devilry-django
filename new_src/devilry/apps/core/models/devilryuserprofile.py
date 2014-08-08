from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


def user_is_basenodeadmin(userobj, *basenode_modelsclasses):
    """
    Check if the given user is admin on any of the given
    ``basenode_modelsclasses``.

    :param basenode_modelsclasses:
        Model classes. They must have an ``admins`` one-to-many relationship
        with User.

    Example (is period admin):

        >>> from devilry.apps.core.models import Period
        >>> from django.contrib.auth.models import User
        >>> donald = User.objects.get(username='donald')
        >>> donald_is_periodadmin = user_is_basenodeadmin(donald, Period)
    """
    for cls in basenode_modelsclasses:
        if cls.objects.filter(admins__id=userobj.id).exists():
            return True
    return False

def user_is_nodeadmin(userobj):
    """
    Check if the given user is admin on any node.
    """
    from .node import Node
    return user_is_basenodeadmin(userobj, Node)

def user_is_subjectadmin(userobj):
    """
    Check if the given user is admin on any subject.
    """
    from .subject import Subject
    return user_is_basenodeadmin(userobj, Subject)

def user_is_periodadmin(userobj):
    """
    Check if the given user is admin on any period.
    """
    from .period import Period
    return user_is_basenodeadmin(userobj, Period)

def user_is_assignmentadmin(userobj):
    """
    Check if the given user is admin on any assignment.
    """
    from .assignment import Assignment
    return user_is_basenodeadmin(userobj, Assignment)



def user_is_admin(userobj):
    """
    Check if the given user is admin on any node, subject, period or
    assignment.
    """
    from .node import Node
    from .subject import Subject
    from .period import Period
    from .assignment import Assignment
    return user_is_basenodeadmin(userobj, Node, Subject, Period, Assignment)

def user_is_admin_or_superadmin(userobj):
    """
    Return ``True`` if ``userobj.is_superuser``, and fall back to calling
    :func:`.user_is_admin` if not.
    """
    if userobj.is_superuser:
        return True
    else:
        return user_is_admin(userobj)

def user_is_examiner(userobj):
    """
    Returns ``True`` if the given ``userobj`` is examiner on any AssignmentGroup.
    """
    from .assignment_group import AssignmentGroup
    return AssignmentGroup.published_where_is_examiner(userobj).exists()

def user_is_student(userobj):
    """
    Returns ``True`` if the given ``userobj`` is candidate on any AssignmentGroup.
    """
    from .assignment_group import AssignmentGroup
    return AssignmentGroup.published_where_is_candidate(userobj).exists()


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
        Not required (The UI defaults to the default language)
    """
    user = models.OneToOneField(User) # This field is required, and it must be named ``user`` (because the model is used as a AUTH_PROFILE_MODULE)
    full_name = models.CharField(max_length=300, blank=True, null=True)
    languagecode = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def get_displayname(self):
        """
        Get a name for this user, preferrably the full name, but falls back to username of
        that is unavailable.
        """
        return self.full_name or self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        DevilryUserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
