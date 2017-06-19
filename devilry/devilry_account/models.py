from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext_lazy

from devilry.devilry_account.exceptions import IllegalOperationError


class UserQuerySet(models.QuerySet):
    def prefetch_related_notification_emails(self):
        """
        Use this if need to get efficient access to the primary :class:`.UserEmail`.

        This will add the ``notification_useremail_objects`` attribute to each returned
        :class:`.User`. ``notification_useremail_objects`` is a list that you can use
        if you need access to the :class:`.UserEmail` objects.
        Use :meth:`.User.notification_emails` to access the emails as a list of
        strings.
        """
        return self.prefetch_related(
                models.Prefetch('useremail_set',
                                queryset=UserEmail.objects.filter(use_for_notifications=True),
                                to_attr='notification_useremail_objects'))

    def prefetch_related_primary_email(self):
        """
        Use this if need to get efficient access to the primary :class:`.UserEmail`.

        This will add the ``primary_useremail_objects`` attribute to each returned
        :class:`.User`. ``primary_useremail_objects`` is a list, and you should not
        use it directly. Use :meth:`.User.primary_useremail_object` or
        :meth:`.User.primary_email` to access the primary email.
        """
        return self.prefetch_related(
                models.Prefetch('useremail_set',
                                queryset=UserEmail.objects.filter(is_primary=True),
                                to_attr='primary_useremail_objects'))

    def prefetch_related_primary_username(self):
        """
        Use this if need to get efficient access to the primary :class:`.UserName`.

        This will add the ``primary_username_objects`` attribute to each returned
        :class:`.User`. ``primary_username_objects`` is a list, and you should not
        use it directly. Use :meth:`.User.primary_username_object` or
        :meth:`.User.primary_username` to access the primary username.
        """
        return self.prefetch_related(
                models.Prefetch('username_set',
                                queryset=UserName.objects.filter(is_primary=True),
                                to_attr='primary_username_objects'))

    def filter_by_emails(self, emails):
        """
        Filter the queryset to only include users with email address
        in the ``emails`` iterable.
        """
        return self.filter(useremail__email__in=emails).distinct()

    def filter_by_usernames(self, usernames):
        """
        Filter the queryset to only include users with username
        in the ``usernames`` iterable.
        """
        return self.filter(username__username__in=usernames).distinct()


class UserManager(BaseUserManager):
    """
    Manager for :class:`User`.
    """
    use_for_related_fields = True

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    #
    #
    # From the QuerySet
    #
    #

    def prefetch_related_notification_emails(self):
        """
        See :meth:`.UserQuerySet.prefetch_related_notification_emails`.
        """
        return self.get_queryset().prefetch_related_notification_emails()

    def prefetch_related_primary_email(self):
        """
        See :meth:`.UserQuerySet.prefetch_related_primary_email`.
        """
        return self.get_queryset().prefetch_related_primary_email()

    def prefetch_related_primary_username(self):
        """
        See :meth:`.UserQuerySet.prefetch_related_primary_username`.
        """
        return self.get_queryset().prefetch_related_primary_username()

    def filter_by_emails(self, emails):
        """
        See :meth:`.UserQuerySet.filter_by_emails`.
        """
        return self.get_queryset().filter_by_emails(emails)

    def filter_by_usernames(self, usernames):
        """
        See :meth:`.UserQuerySet.filter_by_usernames`.
        """
        return self.get_queryset().filter_by_usernames(usernames)

    #
    #
    # Manager-specific methods
    #
    #

    def user_is_basenodeadmin(self, user, *basenode_modelsclasses):
        """
        Check if the given user is admin on any of the given
        ``basenode_modelsclasses``.

        :param basenode_modelsclasses:
            Model classes. They must have an ``admins`` one-to-many relationship
            with User.
        """
        for cls in basenode_modelsclasses:
            if cls.objects.filter(admins__id=user.id).exists():
                return True
        return False

    def user_is_admin(self, user):
        """
        Check if the given user is admin on any subject or period.
        """
        return PermissionGroupUser.objects.filter(user=user).exists()

    def user_is_admin_or_superuser(self, user):
        """
        Return ``True`` if ``user.is_superuser``, and fall back to calling
        :func:`.user_is_admin` if not.
        """
        if user.is_superuser:
            return True
        else:
            return self.user_is_admin(user)

    def user_is_examiner(self, user):
        """
        Returns ``True`` if the given ``user`` is examiner on any AssignmentGroup.
        """
        from devilry.apps.core.models.assignment_group import AssignmentGroup
        return AssignmentGroup.objects.filter_examiner_has_access(user).exists()

    def user_is_student(self, user):
        """
        Returns ``True`` if the given ``user`` is candidate on any AssignmentGroup.
        """
        from devilry.apps.core.models.assignment_group import AssignmentGroup
        return AssignmentGroup.objects.filter_student_has_access(user).exists()

    def create_user(self, username='', email='', password=None, **kwargs):
        """
        Create a new user.

        Requires ``username`` or ``email``, and both can be supplied.
        If ``username`` is supplied, we create a UserName object with ``is_primary=True``,
        and if ``email`` is supplied, we create a UserEmail object with
        ``use_for_notifications=True``.

        If ``password`` is supplied, we set the password, otherwise we
        set an unusable password.

        Other than that, you can provide any :class:`.User` fields except
        ``shortname``. ``shortname`` is created from username or email (in that order).
        """
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND and username:
            raise IllegalOperationError('Can not create user with username when the '
                                        'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND-setting is True')
        shortname = username or email
        user = self.model(shortname=shortname, **kwargs)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        if username:
            user.username_set.create(username=username, is_primary=True)

        if username and not email:
            if getattr(settings, 'DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX', None):
                email = u'{}{}'.format(username, settings.DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX)

        if email:
            user.useremail_set.create(email=email, is_primary=True,
                                      use_for_notifications=True)
        return user

    def get_user(self, username='', email=''):
        if not username and not email:
            raise ValueError('username or email must be supplied')
        if username:
            return self.get_by_username(username=username)
        else:
            return self.get_by_email(email=email)

    def get_or_create_user(self, username='', email='', password=None, **kwargs):
        if not username and not email:
            raise ValueError('username or email must be supplied')
        try:
            user = self.get_user(username=username, email=email)
        except self.model.DoesNotExist:
            user = None

        if user:
            return user, False
        return self.create_user(username=username, email=email, password=password, **kwargs), True

    def create_superuser(self, password=None, **kwargs):
        """
        Create a new superuser.
        """
        email = kwargs.pop(User.USERNAME_FIELD)
        user = self.create_user(email=email, password=password, is_superuser=True, **kwargs)
        return user

    def get_by_email(self, email):
        """
        Get a user by any of their emails.

        Raises:
            User.DoesNotExist: If no :class:`.UserEmail` with the given email is found.
        Returns:
            User: The user object.
        """
        return self.get_queryset().filter(useremail__email=email).get()

    def get_by_username(self, username):
        """
        Get a user by any of their username.

        Raises:
            User.DoesNotExist: If no :class:`.UserName` with the given username is found.
        Returns:
            User: The user object.
        """
        return self.get_queryset().filter(username__username=username).get()

    def __create_primary_useremail_objects_from_users(self, users):
        """
        Create :class:`.UserEmail` objects for the given iterable of
        :class:`.User` objects.

        Uses the ``shortname`` as email, and the UserEmail objects
        is all marked as primary emails, and as notification
        emails.
        """
        new_useremail_objects = []
        for user in users:
            new_username_object = UserEmail(user=user,
                                            email=user.shortname,
                                            is_primary=True,
                                            use_for_notifications=True)
            new_useremail_objects.append(new_username_object)
        UserEmail.objects.bulk_create(new_useremail_objects)

    def bulk_create_from_emails(self, emails):
        """
        Bulk create users for all the emails
        in the given ``emails`` iterator.

        All users is created with unusable password.

        We create a :class:`.UserEmail` object for each of the created
        users. This UserEmail object has ``is_primary`` set to ``True``.

        Raises:
            devilry_account.exceptions.IllegalOperationError: If the
            ``DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND``-setting is ``False``.

        Returns:
            A ``(created_users, excluded_emails)``-tuple.

            ``created_users`` is a queryset with the created users.

            ``excluded_emails`` is a set of the emails that already existed.
        """
        if not settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            raise IllegalOperationError('You can not use bulk_create_from_emails() when '
                                        'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND is False.')
        existing_emails = set(UserEmail.objects.filter(email__in=emails).values_list('email', flat=True))
        existing_shortnames = set(User.objects.filter(shortname__in=emails).values_list('shortname', flat=True))
        existing_emails = existing_emails.union(existing_shortnames)

        all_emails_set = set(emails)
        new_emails_set = all_emails_set.difference(existing_emails)

        new_user_objects = []
        for email in new_emails_set:
            new_user = User(shortname=email)
            new_user.set_unusable_password()
            new_user_objects.append(new_user)
        User.objects.bulk_create(new_user_objects)
        created_users = User.objects.filter(shortname__in=new_emails_set)

        self.__create_primary_useremail_objects_from_users(created_users)

        return created_users, existing_emails

    def __create_primary_username_objects_from_users(self, users):
        """
        Create :class:`.UserName` objects for the given iterable of
        :class:`.User` objects.

        Uses the ``shortname`` as username, and the UserName objects
        is all marked as primary usernames.
        """
        new_username_objects = []
        for user in users:
            new_username_object = UserName(username=user.shortname, is_primary=True, user=user)
            new_username_objects.append(new_username_object)
        UserName.objects.bulk_create(new_username_objects)

    def __create_primary_useremail_objects_from_users_via_suffix(self, users):
        """
        Create :class:`.UserEmail` objects for the given iterable of
        :class:`.User` objects.

        Uses the ``shortname@<settings.DEVILRY_DEFAULT_EMAIL_SUFFIX>`` as email,
        and the UserEmail objects is all marked as primary emails, and as notification
        emails.
        """
        new_useremail_objects = []
        for user in users:
            new_username_object = UserEmail(
                    user=user,
                    email=u'{}{}'.format(user.shortname, settings.DEVILRY_DEFAULT_EMAIL_SUFFIX),
                    is_primary=True,
                    use_for_notifications=True)
            new_useremail_objects.append(new_username_object)
        UserEmail.objects.bulk_create(new_useremail_objects)

    def bulk_create_from_usernames(self, usernames):
        """
        Bulk create users for all the usernames
        in the given ``usernames`` iterator.

        All users is created with unusable password.

        We create a :class:`.UserName` object for each of the created
        users. This UserName object has ``is_primary`` set to ``True``.

        Raises:
            devilry_account.exceptions.IllegalOperationError: If the
            ``DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND``-setting is ``True``.

        Returns:
            A ``(created_users, excluded_usernames)``-tuple.

            ``created_users`` is a queryset with the created users.

            ``excluded_usernames`` is a set of the usernames that already existed.
        """
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            raise IllegalOperationError('You can not use bulk_create_from_usernames() when '
                                        'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND is True.')
        existing_usernames = set(UserName.objects.filter(username__in=usernames).values_list('username', flat=True))
        existing_shortnames = set(User.objects.filter(shortname__in=usernames).values_list('shortname', flat=True))
        existing_usernames = existing_usernames.union(existing_shortnames)

        all_usernames_set = set(usernames)
        new_usernames_set = all_usernames_set.difference(existing_usernames)

        new_user_objects = []
        for username in new_usernames_set:
            new_user = User(shortname=username)
            new_user.set_unusable_password()
            new_user_objects.append(new_user)
        User.objects.bulk_create(new_user_objects)
        created_users = User.objects.filter(shortname__in=new_usernames_set)

        self.__create_primary_username_objects_from_users(created_users)
        if settings.DEVILRY_DEFAULT_EMAIL_SUFFIX:
            self.__create_primary_useremail_objects_from_users_via_suffix(created_users)

        return created_users, existing_usernames


class User(AbstractBaseUser):
    """
    User model for Devilry.
    """
    objects = UserManager()

    #: Is this user a superuser?
    is_superuser = models.BooleanField(
            verbose_name=_('superuser status'),
            default=False,
            help_text=_('Designates that this user has all permissions without '
                        'explicitly assigning them.'))

    #: Short name for the user.
    #: This will be set to the primary email address or to the primary username
    #: depending on the auth backend.
    #: Must be unique.
    shortname = models.CharField(
            max_length=255,
            blank=False, null=False,
            editable=True,
            unique=True,
            help_text=_('The short name for the user. This is set automatically to the '
                        'email or username depending on the method used for authentication.')
    )

    #: Full name of the user. Optional.
    fullname = models.TextField(
            verbose_name=_('Full name'),
            blank=True, default="", null=False)

    #: The last name of the user. Optional.
    #: Used to sort by last name.
    lastname = models.TextField(
            verbose_name=_('Last name'),
            blank=True, default="", null=False)

    #: The datetime the user was created.
    datetime_joined = models.DateTimeField(
            verbose_name=_('date joined'),
            default=timezone.now)

    #: Datetime when this account was suspended.
    suspended_datetime = models.DateTimeField(
            null=True, blank=True,
            verbose_name=_('Suspension time'),
            help_text=_('Time when the account was suspended'))

    #: Reason why the account is suspended.
    suspended_reason = models.TextField(
            blank=True, default='',
            verbose_name=_('Reason for suspension'))

    #: The language code for the preferred language for the user.
    languagecode = models.CharField(
            max_length=10, blank=True, null=False,
            default='',
            verbose_name=_('Preferred language')
    )

    USERNAME_FIELD = 'shortname'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_active(self):
        return self.suspended_datetime is None

    def get_full_name(self):
        """
        Get the :obj:`~.User.fullname`, falling back to :obj:`~.User.shortname`
        if fullname is not set.
        """
        return self.fullname or self.shortname

    def get_short_name(self):
        """
        Get the short name for the user.
        """
        return self.shortname

    def get_displayname(self):
        """
        Get as much of the name as possible. If we have only
        shortname, return that, if we have both shortname and
        fullname, return ``<fullname> (<shortname>)``.
        """
        if self.fullname:
            return u'{} ({})'.format(self.fullname, self.shortname)
        else:
            return self.shortname

    def has_module_perms(self, *args, **kwargs):
        return self.is_superuser

    def has_perm(self, *args, **kwargs):
        return self.is_superuser

    def get_all_permissions(self, *args, **kwargs):
        return set()

    def get_group_permissions(self, *args, **kwargs):
        return set()

    def get_user_permissions(self, *args, **kwargs):
        return set()

    def __unicode__(self):
        return self.shortname

    def clean(self):
        if self.suspended_datetime is None and self.suspended_reason != '':
            raise ValidationError(_('Can not provide a reason for suspension when suspension time is blank.'))
        if not self.shortname:
            raise ValidationError(_('Short name is required.'))
        if self.fullname:
            self.lastname = self.fullname.split()[-1]

    @property
    def notification_emails(self):
        """
        Get the notification emails as a list of strings.

        Only works if you have used :meth:`.UserQuerySet.prefetch_related_notification_emails`
        on the queryset.
        """
        return [useremail.email for useremail in self.notification_useremail_objects]

    @property
    def primary_useremail_object(self):
        """
        Get the primary email address of the user as a :class:`.UserEmail` object.

        Only works if you have used :meth:`.UserQuerySet.prefetch_related_primary_email`
        on the queryset.

        Returns ``None`` if we have no primary email.
        """
        try:
            return self.primary_useremail_objects[0]
        except IndexError:
            return None

    @property
    def primary_email(self):
        """
        Get the primary email address of the user as a string.

        Only works if you have used :meth:`.UserQuerySet.prefetch_related_primary_email`
        on the queryset.

        Returns ``None`` if we have no primary email.
        """
        primary_useremail_object = self.primary_useremail_object
        if primary_useremail_object:
            return primary_useremail_object.email
        else:
            return None

    @property
    def primary_username_object(self):
        """
        Get the primary username of the user as a :class:`.UserName` object.

        Only works if you have used :meth:`.UserQuerySet.prefetch_related_primary_username`
        on the queryset.

        Returns ``None`` if we have no primary username.
        """
        try:
            return self.primary_username_objects[0]
        except IndexError:
            return None

    @property
    def primary_username(self):
        """
        Get the primary username of the user as a string.

        Only works if you have used :meth:`.UserQuerySet.prefetch_related_primary_username`
        on the queryset.

        Returns ``None`` if we have no primary username.
        """
        primary_username_object = self.primary_username_object
        if primary_username_object:
            return primary_username_object.username
        else:
            return None


class AbstractUserIdentity(models.Model):
    """
    Base class for :class:`.UserEmail` and :class:`.UserName`.
    """

    class Meta:
        abstract = True

    #: Foreign key to the user owning this email address.
    user = models.ForeignKey(User)

    #: The datetime when this was created.
    created_datetime = models.DateTimeField(
            default=timezone.now,
            editable=False,
            null=False, blank=False)

    #: The datetime when this was last updated.
    last_updated_datetime = models.DateTimeField(
            default=timezone.now,
            editable=False,
            null=False, blank=False)

    def clean(self):
        self.last_updated_datetime = timezone.now()


class UserEmail(AbstractUserIdentity):
    """
    Stores a single email address for a :class:`.User`.
    """

    class Meta:
        verbose_name = _('Email address')
        verbose_name_plural = _('Email addresses')
        unique_together = [
            ('user', 'is_primary')
        ]

    #: The email address of the user.
    #: Must be unique.
    email = models.EmailField(
            verbose_name=_('Email'),
            unique=True,
            max_length=255)

    #: Is this a notification email for the user?
    #: A user can have multiple notification emails.
    use_for_notifications = models.BooleanField(
            default=True,
            verbose_name=_('Send notifications to this email address?'))

    #: Is this the primary email for the user?
    #: Valid values are: ``None`` and ``True``, and only
    #: one UserEmail per user can have ``is_primary=True``.
    is_primary = models.NullBooleanField(
            verbose_name=_('Is this your primary email?'),
            choices=[
                (None, _('No')),
                (True, _('Yes'))
            ],
            help_text=_('Your primary email is the email address used when we '
                        'need to display a single email address.')
    )

    def clean(self):
        if self.is_primary is False:
            raise ValidationError('is_primary can not be False. Valid values are: True, None.')
        if self.is_primary:
            other_useremails = UserEmail.objects.filter(user=self.user)
            if self.id is not None:
                other_useremails = other_useremails.exclude(id=self.id)
            other_useremails.update(is_primary=None)

            if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
                user = self.user
                if user.shortname != self.email:
                    user.shortname = self.email
                    user.save()

    def __unicode__(self):
        return _('%(email)s - User%(userid)s') % {
            'email': self.email,
            'userid': self.user_id
        }


class UserName(AbstractUserIdentity):
    """
    Stores a single username for a :class:`.User`.

    The username is used for login, and the primary username
    is synced into :obj:`.User.shortname`.
    """

    class Meta:
        verbose_name = _('Username')
        verbose_name_plural = _('Usernames')
        unique_together = [
            ('user', 'is_primary')
        ]

    #: The username of the user.
    #: Must be unique.
    username = models.CharField(
            verbose_name=_('Username'),
            unique=True,
            max_length=255)

    #: Is this the primary username for the user?
    #: Valid values are: ``None`` and ``True``, and only
    #: one UserName per user can have ``is_primary=True``.
    is_primary = models.NullBooleanField(
            verbose_name=_('Is this your primary username?'),
            choices=[
                (None, _('No')),
                (True, _('Yes'))
            ],
            help_text=_('Your primary username is shown alongside your full '
                        'name to identify you to teachers, examiners and '
                        'other students.')
    )

    def clean(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            raise ValidationError('Can not create UserName objects when the '
                                  'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND is True.')
        if self.is_primary is False:
            raise ValidationError('is_primary can not be False. Valid values are: True, None.')
        if self.is_primary:
            other_usernames = UserName.objects.filter(user=self.user)
            if self.id is not None:
                other_usernames = other_usernames.exclude(id=self.id)
            other_usernames.update(is_primary=None)

            user = self.user
            if user.shortname != self.username:
                user.shortname = self.username
                user.save()

    def __unicode__(self):
        return _('%(username)s - User%(userid)s') % {
            'username': self.username,
            'userid': self.user_id
        }


class PermissionGroupUser(models.Model):
    """
    Defines the many-to-many relationship between :class:`.User`
    and :class:`.PermissionGroup`.
    """

    class Meta:
        verbose_name = _('Permission group user')
        verbose_name_plural = _('Permission group users')
        unique_together = (
            ('permissiongroup', 'user'),
        )

    #: The group.
    permissiongroup = models.ForeignKey('devilry_account.PermissionGroup')

    #: The user.
    user = models.ForeignKey(User)

    def __unicode__(self):
        return _('%(user)s in group %(permissiongroup)s') % {
            'user': self.user.shortname,
            'permissiongroup': self.permissiongroup.name,
        }


class PermissionGroup(models.Model):
    """
    Permission group data model.

    Each group has a :obj:`~.PermissionGroup.grouptype` which determines
    the type of objects it can be added to.
    """

    #: The value for :obj:`~.PermissionGroup.grouptype` that identifies the group as
    #: a departmentadmin permission group.
    GROUPTYPE_DEPARTMENTADMIN = 'departmentadmin'

    #: The value for :obj:`~.PermissionGroup.grouptype` that identifies the group as
    #: a subjectadmin permission group.
    GROUPTYPE_SUBJECTADMIN = 'subjectadmin'

    #: The value for :obj:`~.PermissionGroup.grouptype` that identifies the group as
    #: a periodadmin permission group.
    GROUPTYPE_PERIODADMIN = 'periodadmin'

    #: Choices for :obj:`~.PermissionGroup.grouptype`.
    GROUPTYPE_CHOICES = (
        (GROUPTYPE_DEPARTMENTADMIN, _('Department administrator group')),
        (GROUPTYPE_SUBJECTADMIN, _('Course administrator group')),
        (GROUPTYPE_PERIODADMIN, _('Semester administrator group')),
    )

    class Meta:
        verbose_name = _('Permission group')
        verbose_name_plural = _('Permission group')

    #: The name of the group. Must be unique.
    name = models.CharField(
            max_length=255,
            null=False, blank=False, unique=True,
            verbose_name=_('Name'),
            help_text=_('A unique name for this group.'))

    #: The time this group was created.
    created_datetime = models.DateTimeField(
            null=False, auto_now_add=True,
            editable=False,
            verbose_name=_('Created time'),
            help_text=_('The time when this group was created.'))

    #: Last time this group was updated.
    updated_datetime = models.DateTimeField(
            null=False, auto_now=True,
            editable=False,
            verbose_name=_('Last updated time'),
            help_text=_('The time when this group last updated.'))

    #: Last time this group was updated from a third party sync system.
    syncsystem_update_datetime = models.DateTimeField(
            null=True,
            editable=False,
            verbose_name=_('Last updated from syncsystem time'),
            help_text=_('The time when this group last updated from a third party sync system.'))

    #: The grouptype determines what kind of object a group can be added to:
    #:
    #: - ``subjectadmin``: Can be assigned to **a single** :class:`devilry.apps.core.models.Subject`.
    #: - ``periodadmin``: Can be assigned to **a single** :class:`devilry.apps.core.models.Period`.
    #: - ``departmentadmin``: Can be assigned to multiple :class:`devilry.apps.core.models.Subject`.
    grouptype = models.CharField(
            max_length=30,
            choices=GROUPTYPE_CHOICES,
            null=False, blank=False,
            verbose_name=_('Permission group type'),
            help_text=_('Course and semester administrator groups can only be assigned to a single '
                        'course or semester. Department administrator groups can be assigned to multiple '
                        'courses. You can not change this for existing permission groups.')
    )

    #: Is this group manageable by normal admins?
    #:
    #: Only superusers can edit the group
    #: if this is ``False``. Use cases for setting this to ``False``:
    #:
    #: - Superusers want to create groups that they have full control over.
    #: - Groups imported from a third party sync system.
    #:
    #: If grouptype is ``departmentadmin``, this can not be ``True``.
    is_custom_manageable = models.BooleanField(
            default=False,
            verbose_name=_('Custom manageable?'),
            help_text=_('Is this group mageable by non-superusers. Can not be enabled for '
                        'department administrator groups.')
    )

    #: Users belonging to this group.
    users = models.ManyToManyField(
            through=PermissionGroupUser,
            to=User,
            verbose_name=_('Users in this group'),
            blank=True)

    def __unicode__(self):
        return u'{name} ({grouptype})'.format(
            name=self.name,
            grouptype=self.get_grouptype_display()
        )

    def clean(self):
        if self.grouptype == self.GROUPTYPE_DEPARTMENTADMIN and self.is_custom_manageable:
            raise ValidationError(_('Department administrator groups can not be '
                                    'custom manageable.'))
        if self.id is not None:
            currently_stored_group = PermissionGroup.objects.get(id=self.id)
            if currently_stored_group.grouptype != self.grouptype:
                raise ValidationError(_('Permission group type can not be changed.'))


class PeriodPermissionGroupQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.PeriodPermission`.
    """
    def user_is_periodadmin_for_period(self, user, period):
        """
        Find out if the given ``user`` is ``"periodadmin"`` on the given ``period``.

        You normally do not use this directly, but use :meth:`.get_devilryrole_for_user_on_period`.

        Args:
            period: A :class:`devilry.apps.core.models.Subject` object.
            user: A User object.

        Returns:
            bool: ``True`` if the given user is periodadmin on the given period,
            otherwise it returns ``False``.
        """
        return PeriodPermissionGroup.objects \
            .filter(permissiongroup__users=user,
                    period=period)\
            .exists()

    def get_devilryrole_for_user_on_period(self, user, period):
        """
        Get the devilryrole for the given ``user`` on the given ``period``.

        .. seealso:: If you need to find the same information for a subject,
            use :meth:`.SubjectPermissionGroupQuerySet.get_devilryrole_for_user_on_subject`.

        Args:
            period: A :class:`devilry.apps.core.models.Subject` object.
            user: A User object.

        Returns:
            str: One of the following looked up in the listed order:

            - ``"departmentadmin"``: If the user is superuser or in a
              :class:`.SubjectPermissionGroup` with :obj:`.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN`
              for the subject owning the period.
            - ``"subjectadmin"``: If the user is in a
              :class:`.SubjectPermissionGroup` with :obj:`.PermissionGroup.GROUPTYPE_SUBJECTADMIN`
              for the subject owning the period.
            - ``"periodadmin"``: If the user is in a :class:`.PeriodPermissionGroup` for the period.
            - ``None``: If no of the conditions listed above is met.
        """
        devilryrole = SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
            user=user, subject=period.subject)
        if devilryrole:
            return devilryrole
        elif self.user_is_periodadmin_for_period(user=user, period=period):
            return 'periodadmin'
        else:
            return None

    def get_custom_managable_periodpermissiongroup_for_period(self, period):
        """
        Get the PeriodPermissionGroup where :obj:`.PermissionGroup.is_custom_manageable` is ``True``
        for the given ``period``.

        Each :class:`devilry.apps.core.models.Period` has exactly one custom managable
        :class:`.PermissionGroup`, which is the permission group where admins added
        by non-superusers via the admin UI are added.

        .. note:: The queryset used does ``select_related('permissiongroup')``, so looking
            up permissiongroup for the returned PeriodPermissionGroup does not require
            an extra database query.

        Args:
            period: A :class:`devilry.apps.core.models.Period` object.

        Raises:
            PeriodPermissionGroup.DoesNotExist: If no custom managable PermissionGroup exists for
                the given period.
        """
        return self.filter(period=period, permissiongroup__is_custom_manageable=True)\
            .select_related('permissiongroup')\
            .get()


class PeriodPermissionGroup(models.Model):
    """
    Defines the many-to-many relationship between
    :class:`devilry.apps.core.Period` and :class:`.PermissionGroup`.
    """
    objects = PeriodPermissionGroupQuerySet.as_manager()

    class Meta:
        verbose_name = _('Semester permission group')
        verbose_name_plural = _('Semester permission groups')
        unique_together = (
            ('permissiongroup', 'period'),
        )

    #: The group.
    permissiongroup = models.ForeignKey('devilry_account.PermissionGroup')

    #: The :class:`devilry.apps.core.Period`.
    period = models.ForeignKey('core.Period')

    def __unicode__(self):
        if self.permissiongroup.is_custom_manageable:
            return ugettext_lazy('Semester administrators for %(period)s') % {
                'period': self.period.get_path(),
            }
        else:
            return self.permissiongroup.name

    def clean(self):
        if self.permissiongroup.grouptype != PermissionGroup.GROUPTYPE_PERIODADMIN:
            raise ValidationError(_(
                    'Only semesters can be added to semester administrator permission groups.'))
        if self.permissiongroup.is_custom_manageable:
            queryset = PeriodPermissionGroup.objects \
                .filter(permissiongroup=self.permissiongroup)
            if self.id is not None:
                queryset = queryset.exclude(id=self.id)
            if queryset.exists():
                raise ValidationError(_('Only a single editable permission group '
                                        'is allowed for a semester.'))


class SubjectPermissionGroupQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.SubjectPermission`.
    """

    def __user_is_admin_on_subjectpermissiongroup(self, user, subject, grouptype):
        return SubjectPermissionGroup.objects \
            .filter(permissiongroup__users=user,
                    permissiongroup__grouptype=grouptype,
                    subject=subject)\
            .exists()

    def user_is_departmentadmin_for_subject(self, user, subject):
        """
        Find out if the given ``user`` is ``"departmentadmin"`` on the given ``subject``.

        You normally do not use this directly, but use :meth:`.get_devilryrole_for_user_on_subject`.

        Args:
            subject: A :class:`devilry.apps.core.models.Subject` object.
            user: A User object.

        Returns:
            bool: ``True`` if the given user is departmentadmin on the given subject,
            otherwise it returns ``False``.
        """
        return self.__user_is_admin_on_subjectpermissiongroup(
            user=user,
            subject=subject,
            grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN
        )

    def user_is_subjectadmin_for_subject(self, user, subject):
        """
        Find out if the given ``user`` is ``"subjectadmin"`` on the given ``subject``.

        This does not take higher permissions into consideration, so you
        should check if the user is departmentadmin with :meth:`.user_is_departmentadmin_for_subject`
        if you want to find the highest permission for the user.

        You normally do not use this directly, but use :meth:`.get_devilryrole_for_user_on_subject`.

        Args:
            subject: A :class:`devilry.apps.core.models.Subject` object.
            user: A User object.

        Returns:
            bool: ``True`` if the given user is subjectadmin on the given subject,
            otherwise it returns ``False``.
        """
        return self.__user_is_admin_on_subjectpermissiongroup(
            user=user,
            subject=subject,
            grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN
        )

    def get_devilryrole_for_user_on_subject(self, user, subject):
        """
        Get the devilryrole for the given ``user`` on the given ``subject``.

        .. seealso:: If you need to find the same information for a period,
            use :meth:`.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`.

        Args:
            subject: A :class:`devilry.apps.core.models.Subject` object.
            user: A User object.

        Returns:
            str: One of the following looked up in the listed order:

            - ``"departmentadmin"``: If the user is superuser or in a
              :class:`.SubjectPermissionGroup` with :obj:`.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN`
              for the subject owning the period.
            - ``"subjectadmin"``: If the user is in a
              :class:`.SubjectPermissionGroup` with :obj:`.PermissionGroup.GROUPTYPE_SUBJECTADMIN`
              for the subject owning the period.
            - ``None``: If no of the conditions listed above is met.
        """
        if user.is_superuser or self.user_is_departmentadmin_for_subject(user=user, subject=subject):
            return 'departmentadmin'
        elif self.user_is_subjectadmin_for_subject(user=user, subject=subject):
            return 'subjectadmin'
        else:
            return None

    def get_custom_managable_subjectpermissiongroup_for_subject(self, subject):
        """
        Get the SubjectPermissionGroup where :obj:`.PermissionGroup.is_custom_manageable` is ``True``
        for the given ``subject``.

        Each :class:`devilry.apps.core.models.Subject` has exactly one custom managable
        :class:`.PermissionGroup`, which is the permission group where admins added
        by non-superusers via the admin UI are added.

        .. note:: The queryset used does ``select_related('permissiongroup')``, so looking
            up permissiongroup for the returned SubjectPermissionGroup does not require
            an extra database query.

        Args:
            subject: A :class:`devilry.apps.core.models.Subject` object.

        Raises:
            SubjectPermissionGroup.DoesNotExist: If no custom managable PermissionGroup exists for
                the given subject.
        """
        return self.filter(subject=subject, permissiongroup__is_custom_manageable=True)\
            .select_related('permissiongroup')\
            .get()


class SubjectPermissionGroup(models.Model):
    """
    Defines the many-to-many relationship between
    :class:`devilry.apps.core.Subject` and :class:`.PermissionGroup`.
    """
    objects = SubjectPermissionGroupQuerySet.as_manager()

    class Meta:
        verbose_name = _('Course permission group')
        verbose_name_plural = _('Course permission groups')
        unique_together = (
            ('permissiongroup', 'subject'),
        )

    #: The permissiongroup.
    permissiongroup = models.ForeignKey('devilry_account.PermissionGroup')

    #: The :class:`devilry.apps.core.Subject`.
    subject = models.ForeignKey('core.Subject')

    def __unicode__(self):
        if self.permissiongroup.is_custom_manageable:
            return ugettext_lazy('Course administrators for %(subject)s') % {
                'subject': self.subject.short_name,
            }
        else:
            return self.permissiongroup.name

    def clean(self):
        if self.permissiongroup.grouptype not in [PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                                  PermissionGroup.GROUPTYPE_DEPARTMENTADMIN]:
            raise ValidationError(_(
                    'Courses can only be added to subject and department administrator permission groups.'))
        if self.permissiongroup.is_custom_manageable:
            queryset = SubjectPermissionGroup.objects \
                .filter(permissiongroup=self.permissiongroup)
            if self.id is not None:
                queryset = queryset.exclude(id=self.id)
            if queryset.exists():
                raise ValidationError(_('Only a single editable permission group '
                                        'is allowed for a course.'))
