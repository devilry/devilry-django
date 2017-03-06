import re
import warnings

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy

from abstract_applicationkeyvalue import AbstractApplicationKeyValue
from abstract_is_admin import AbstractIsAdmin
from devilry.devilry_account.models import User
from node import Node
from period import Period
import period_tag


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

    #: Automatic anonymous ID for a student/examiner for the entire semester.
    automatic_anonymous_id = models.CharField(max_length=255,
                                              blank=True, null=False, default='',
                                              editable=False)

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
        return '{}#{} on {}'.format(self.__class__.__name__,
                                    self.user.shortname,
                                    self.period.get_path())


class RelatedExaminerManager(AbstractRelatedUserManager):
    """
    Manager for :class:`.RelatedExaminer`.
    """
    use_for_related_fields = True


class RelatedExaminerQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.RelatedExaminer`.
    """
    def annotate_with_number_of_groups_on_assignment(self, assignment):
        """
        Annotates the queryset with number of :class:`devilry.apps.core.models.AssignmentGroup`
        objects where the RelatedExaminer is :class:`devilry.apps.core.models.Examiner` within the given
        assignment.

        Args:
            assignment: A :class:`devilry.apps.core.models.Assignment` object.
        """
        return self.annotate(
            number_of_groups_on_assignment=models.Count(
                models.Case(
                    models.When(examiner__assignmentgroup__parentnode=assignment,
                                then=1)
                )
            )
        )

    def extra_annotate_with_number_of_candidates_on_assignment(self, assignment):
        """
        Annotates the queryset with number of :class:`devilry.apps.core.models.Candidate`
        objects within all :class:`devilry.apps.core.models.AssignmentGroup` objects where
        the RelatedExaminer is :class:`devilry.apps.core.models.Examiner` within the given
        assignment.

        Args:
            assignment: A :class:`devilry.apps.core.models.Assignment` object.
        """
        return self.extra(
            select={
                'number_of_candidates_on_assignment': """
                    SELECT
                        COUNT(core_candidate.id)
                    FROM core_candidate
                    INNER JOIN core_assignmentgroup
                        ON (core_assignmentgroup.id = core_candidate.assignment_group_id)
                    WHERE
                        core_assignmentgroup.parentnode_id = %s
                        AND
                        core_candidate.assignment_group_id IN (
                            SELECT core_assignmentgroup_examiners.assignmentgroup_id
                            FROM core_assignmentgroup_examiners
                            WHERE
                                core_assignmentgroup_examiners.relatedexaminer_id = core_relatedexaminer.id
                                AND
                                core_assignmentgroup.id = core_assignmentgroup_examiners.assignmentgroup_id
                        )
                """
            },
            select_params=[
                assignment.id
            ]
        )


class RelatedExaminer(RelatedUserBase):
    """ Related examiner.

    Adds no fields to RelatedUserBase.
    """
    objects = RelatedExaminerManager.from_queryset(RelatedExaminerQuerySet)()

    #: Setting this to ``False`` indicates that the examiner is deleted from the course
    #: for this period. All access is removed.
    active = models.BooleanField(default=True)

    def get_anonymous_name(self):
        """
        Get the anonymous name for this RelatedExaminer.

        If :obj:`~.RelatedUser.automatic_anonymous_id` is set,
        falling back on ``"Anonymous ID missing"``.

        Returns:
            str: A unicode string with the anonymous name.
        """
        if self.automatic_anonymous_id:
            return self.automatic_anonymous_id
        else:
            return ugettext_lazy('Anonymous ID missing')

    @property
    def relatedusertag_set(self):
        return self.relatedexaminertag_set


class RelatedStudentQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.RelatedStudent`.
    """
    def get_userid_to_candidateid_map(self):
        """
        Get a dict mapping user ID to candidate ID.
        """
        queryset = self.exclude(models.Q(candidate_id='') | models.Q(candidate_id=None))
        return dict(queryset.values_list('user_id', 'candidate_id'))

    def prefetch_syncsystemtag_objects(self):
        """
        Prefetch :class:`.RelatedStudentSyncSystemTag` objects in the
        ``syncsystemtag_objects`` attribute.

        The ``syncsystemtag_objects`` attribute is a ``list`` of
        :class:`.RelatedStudentSyncSystemTag` objects ordered by
        ``tag`` in ascending order.
        """
        warnings.warn('deprecated, function up to date but will be refactored', DeprecationWarning)
        return self.prefetch_related(
            models.Prefetch('periodtag_set',
                            queryset=period_tag.PeriodTag.objects.order_by('tag'),
                            to_attr='syncsystemtag_objects'))


class RelatedStudentManager(AbstractRelatedUserManager):
    """
    Manager for :class:`.RelatedStudent`.
    """
    use_for_related_fields = True


class RelatedStudent(RelatedUserBase):
    """
    Related student.
    """
    objects = RelatedStudentManager.from_queryset(RelatedStudentQuerySet)()

    #: Setting this to ``False`` indicates that the student has dropped out
    #: or been kicked out of the course for this period.
    active = models.BooleanField(default=True)

    #: A candidate ID that follows the student through the entire period.
    candidate_id = models.CharField(max_length=30, blank=True, null=True)

    def get_anonymous_name(self):
        """
        Get the anonymous name for this RelatedStudent.

        If :obj:`~.RelatedStudent.candidate_id` is set, we use use that,
        falling back on :obj:`~.RelatedUser.automatic_anonymous_id`, and
        then falling back on ``"Anonymous ID missing"``.

        Returns:
            str: A unicode string with the anonymous name.
        """
        if self.candidate_id:
            return self.candidate_id
        elif self.automatic_anonymous_id:
            return self.automatic_anonymous_id
        else:
            return ugettext_lazy('Anonymous ID missing')

    @property
    def relatedusertag_set(self):
        return self.relatedstudenttag_set

    @property
    def syncsystemtag_stringlist(self):
        """
        A shortcut for getting a list of tag strings from the
        ``syncsystemtag_objects`` list when the queryset uses
        :meth:`.RelatedStudentQuerySet.prefetch_syncsystemtag_objects`.
        """
        if not hasattr(self, 'syncsystemtag_objects'):
            raise AttributeError('The syncsystemtag_stringlist property requires '
                                 'RelatedStudentQuerySet.prefetch_syncsystemtag_objects().')
        return [syncsystemtag.tag for syncsystemtag in self.syncsystemtag_objects]


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
