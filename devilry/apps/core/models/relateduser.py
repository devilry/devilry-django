import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from devilry.devilry_account.models import User

from period import Period
from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_applicationkeyvalue import AbstractApplicationKeyValue


class BulkCreateFromEmailsResult(object):
    """
    Return value of :meth:`.AbstractRelatedUserManager.bulk_create_from_emails`.

    .. attribute:: created_relatedusers_queryset

        Queryset with all the created related users.

    .. attribute:: existing_relateduser_emails_set

        Set of the email of related users that was NOT created.

    .. attribute:: created_users_queryset

        Queryset with all the created users. Warning: this
        **is not** the created **related** users, it is the
        :class:`devilry.devilry_account.User` objects that was
        created.

    .. attribute:: existing_user_emails_set

        Set of the email of the :class:`~devilry.devilry_account.User` objects
        that was NOT created. If all the users already had a User object,
        this will include all the email addresses provided to the method.

    """

    def __init__(self, modelclass, created_users_queryset, existing_user_emails_set,
                 created_relatedusers_queryset,
                 existing_relateduser_emails_set):
        self.__modelclass = modelclass
        self.created_users_queryset = created_users_queryset
        self.existing_user_emails_set = existing_user_emails_set
        self.created_relatedusers_queryset = created_relatedusers_queryset
        self.existing_relateduser_emails_set = existing_relateduser_emails_set

    def new_users_was_created(self):
        return self.created_users_queryset.exists()

    def new_relatedusers_was_created(self):
        return self.created_relatedusers_queryset.exists()

        # def get_existing_relatedusers_queryset(self):
        #     return self.__modelclass.objects.filter(
        #         user__useremail__email__in=self.existing_relateduser_emails_set).distinct()


class BulkCreateFromUsernamesResult(object):
    """
    Return value of :meth:`.AbstractRelatedUserManager.bulk_create_from_usernames`.

    .. attribute:: created_relatedusers_queryset

        Queryset with all the created related users.

    .. attribute:: existing_relateduser_usernames_set

        Set of the username of related users that was NOT created.

    .. attribute:: created_users_queryset

        Queryset with all the created users. Warning: this
        **is not** the created **related** users, it is the
        :class:`devilry.devilry_account.User` objects that was
        created.

    .. attribute:: existing_user_usernames_set

        Set of the username of the :class:`~devilry.devilry_account.User` objects
        that was NOT created. If all the users already had a User object,
        this will include all the username addresses provided to the method.

    """

    def __init__(self, modelclass, created_users_queryset, existing_user_usernames_set,
                 created_relatedusers_queryset,
                 existing_relateduser_usernames_set):
        self.__modelclass = modelclass
        self.created_users_queryset = created_users_queryset
        self.existing_user_usernames_set = existing_user_usernames_set
        self.created_relatedusers_queryset = created_relatedusers_queryset
        self.existing_relateduser_usernames_set = existing_relateduser_usernames_set

    def new_users_was_created(self):
        return self.created_users_queryset.exists()

    def new_relatedusers_was_created(self):
        return self.created_relatedusers_queryset.exists()

        # def get_existing_relatedusers_queryset(self):
        #     return self.__modelclass.objects.filter(
        #         user__username__username__in=self.existing_relateduser_usernames_set).distinct()


class AbstractRelatedUserManager(models.Manager):
    """
    Base class for the managers for related users.
    """

    def bulk_create_from_emails(self, period, emails):
        """
        Bulk create related student/examiner for all the emails in the given ``emails`` iterator.

        Uses :meth:`devilry.devilry_account.models.UserManager.bulk_create_from_emails`
        to create any non-existing users.

        Raises:
            devilry_account.exceptions.IllegalOperationError: If the
                ``DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND``-setting is ``False``.

        Returns:
            :class:`.BulkCreateFromEmailsResult` object with detailed information about
            the created users, created related users, and the users and related users
            that was not created.
        """
        existing_relateduser_emails_set = set(self.model.objects.filter(
            period=period,
            user__useremail__email__in=emails).values_list('user__useremail__email', flat=True))
        all_relateduser_emails_set = set(emails)
        new_relateduser_emails_set = all_relateduser_emails_set.difference(existing_relateduser_emails_set)

        created_users_queryset, existing_user_emails_set = get_user_model().objects.bulk_create_from_emails(
            new_relateduser_emails_set)

        new_relateduser_objects = []
        new_relateduser_users_queryset = get_user_model().objects.filter_by_emails(new_relateduser_emails_set)
        for user in new_relateduser_users_queryset:
            new_relateduser = self.model(period=period, user=user)
            new_relateduser_objects.append(new_relateduser)
        self.model.objects.bulk_create(new_relateduser_objects)
        created_relatedusers_queryset = self.model.objects.filter(
            period=period,
            user__in=new_relateduser_users_queryset)

        return BulkCreateFromEmailsResult(
            modelclass=self.model,
            created_users_queryset=created_users_queryset,
            existing_user_emails_set=existing_user_emails_set,
            created_relatedusers_queryset=created_relatedusers_queryset,
            existing_relateduser_emails_set=existing_relateduser_emails_set)

    def bulk_create_from_usernames(self, period, usernames):
        """
        Bulk create related student/examiner for all the usernames in the given ``usernames`` iterator.

        Uses :meth:`devilry.devilry_account.models.UserManager.bulk_create_from_usernames`
        to create any non-existing users.

        Raises:
            devilry_account.exceptions.IllegalOperationError: If the
                ``DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND``-setting is ``True``.

        Returns:
            :class:`.BulkCreateFromUsernamesResult` object with detailed information about
            the created users, created related users, and the users and related users
            that was not created.
        """
        existing_relateduser_usernames_set = set(self.model.objects.filter(
            period=period,
            user__username__username__in=usernames).values_list('user__username__username', flat=True))
        all_relateduser_usernames_set = set(usernames)
        new_relateduser_usernames_set = all_relateduser_usernames_set.difference(
            existing_relateduser_usernames_set)

        created_users_queryset, existing_user_usernames_set = get_user_model().objects \
            .bulk_create_from_usernames(
            new_relateduser_usernames_set)

        new_relateduser_objects = []
        new_relateduser_users_queryset = get_user_model().objects \
            .filter_by_usernames(new_relateduser_usernames_set)
        for user in new_relateduser_users_queryset:
            new_relateduser = self.model(period=period, user=user)
            new_relateduser_objects.append(new_relateduser)
        self.model.objects.bulk_create(new_relateduser_objects)
        created_relatedusers_queryset = self.model.objects.filter(
            period=period,
            user__in=new_relateduser_users_queryset)

        return BulkCreateFromUsernamesResult(
            modelclass=self.model,
            created_users_queryset=created_users_queryset,
            existing_user_usernames_set=existing_user_usernames_set,
            created_relatedusers_queryset=created_relatedusers_queryset,
            existing_relateduser_usernames_set=existing_relateduser_usernames_set)


class RelatedUserBase(models.Model, AbstractIsAdmin):
    """
    Base class for :class:`devilry.apps.core.models.RelatedStudent` and
    :class:`devilry.apps.core.models.RelatedExaminer`.
    """

    #: The period that the user is related to.
    period = models.ForeignKey(Period,
                               verbose_name='Period',
                               help_text="The period.")

    #: A User object. Must be unique within this
    #: period.
    user = models.ForeignKey(User, help_text="The related user.")

    #: Comma-separated list of tags. Each tag is a word with the following
    #: letters allowed: a-z and 0-9. Each word is separated by a comma, and no
    #: whitespace.
    #:
    #: .. deprecated:: Since 3.0. Use :class:`.RelatedExaminerSyncSystemTag` and
    #:
    #:    :class:`.RelatedStudentSyncSystemTag` instead.
    #:
    tags = models.TextField(blank=True, null=True,
                            help_text="Comma-separated list of tags. Each tag is a word with the following letters "
                                      "allowed: a-z, 0-9, ``_`` and ``-``. Each word is separated by a comma, "
                                      "and no whitespace.")

    tags_patt = re.compile('^(?:[a-z0-9_-]+,)*[a-z0-9_-]+$')

    class Meta:
        abstract = True
        unique_together = ('period', 'user')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(period__admins=user_obj) | \
            Q(period__parentnode__admins=user_obj) | \
            Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def clean(self):
        if self.tags and not self.tags_patt.match(self.tags):
            raise ValidationError('tags must be a comma-separated list of tags, each tag only containing '
                                  'a-z, 0-9, ``_`` and ``-``.')

    def __unicode__(self):
        return '{} #{}'.format(self.__class__.__name__, self.id)


class RelatedExaminerManager(AbstractRelatedUserManager):
    """
    Manager for :class:`.RelatedExaminer`.
    """
    use_for_related_fields = True


class RelatedExaminer(RelatedUserBase):
    """ Related examiner.

    Adds no fields to RelatedUserBase.
    """
    objects = RelatedExaminerManager()


class RelatedStudentQueryset(models.QuerySet):
    """
    QuerySet for :class:`.RelatedStudent`.
    """
    def get_userid_to_candidateid_map(self):
        """
        Get a dict mapping user ID to candidate ID.
        """
        queryset = self.exclude(models.Q(candidate_id='') | models.Q(candidate_id=None))
        return dict(queryset.values_list('user_id', 'candidate_id'))


class RelatedStudentManager(AbstractRelatedUserManager):
    """
    Manager for :class:`.RelatedStudent`.
    """
    use_for_related_fields = True

    def get_queryset(self):
        return RelatedStudentQueryset(self.model, using=self._db)

    def get_userid_to_candidateid_map(self):
        """
        See :meth:`.RelatedStudentQueryset.get_userid_to_candidateid_map`.
        """
        return self.get_queryset().get_userid_to_candidateid_map()


class RelatedStudent(RelatedUserBase):
    """ Related student.

    .. attribute:: candidate_id

        If a candidate has the same Candidate ID for all or many assignments in
        a semester, this field can be set to simplify setting candidate IDs on
        each assignment.
    """
    objects = RelatedStudentManager()

    #: A candidate ID that follows the student through the entire period.
    candidate_id = models.CharField(max_length=30, blank=True, null=True)

    #: Automatic anonymous ID for a student for the entire semester.
    automatic_anonymous_id = models.CharField(max_length=255,
                                              blank=True, null=False, default='',
                                              editable=False)


class RelatedUserSyncSystemTag(models.Model):
    """
    Base class for :class:`.RelatedExaminerSyncSystemTag` and
    :class:`.RelatedExaminerSyncSystemTag`.
    """

    class Meta:
        abstract = True

    #: A tag unique for a the related student/examiner.
    #: Max 15 characters.
    tag = models.CharField(db_index=True, max_length=15)


class RelatedExaminerSyncSystemTag(RelatedUserSyncSystemTag):
    """
    A tag for a :class:`.RelatedStudent`.

    Used by a third-party sync system to organize students.

    We use this as one of the ways admins can auto-assign examiners
    to students (match :class:`.RelatedExaminerSyncSystemTag` to
    :class:`.RelatedExaminerSyncSystemTag`).
    """

    class Meta:
        unique_together = [
            ('relatedexaminer', 'tag')
        ]

    #: Foreignkey to the :class:`.RelatedExaminer` this tag is for.
    relatedexaminer = models.ForeignKey(RelatedExaminer)


class RelatedStudentSyncSystemTag(RelatedUserSyncSystemTag):
    """
    A tag for a :class:`.RelatedStudent`.

    Used by a third-party sync system to organize tag students.

    We use this as one of the ways admins can auto-assign examiners
    to students (match :class:`.RelatedExaminerSyncSystemTag` to
    :class:`.RelatedExaminerSyncSystemTag`).
    """

    class Meta:
        unique_together = [
            ('relatedstudent', 'tag')
        ]

    #: Foreignkey to the :class:`.RelatedStudent` this tag is for.
    relatedstudent = models.ForeignKey(RelatedStudent)


class RelatedStudentKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific RelatedStudent. """
    relatedstudent = models.ForeignKey(RelatedStudent)
    student_can_read = models.BooleanField(
        help_text='Specifies if a student can read the value or not.',
        default=False)

    class Meta:
        unique_together = ('relatedstudent', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return (Q(relatedstudent__period__admins=user_obj) |
                Q(relatedstudent__period__parentnode__admins=user_obj) |
                Q(relatedstudent__period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj)))

    def __unicode__(self):
        return '{0}: {1}'.format(self.relatedstudent, super(RelatedStudentKeyValue, self).__unicode__())
