

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy
from django.utils import timezone

from .abstract_applicationkeyvalue import AbstractApplicationKeyValue
from .abstract_is_admin import AbstractIsAdmin
from .abstract_is_candidate import AbstractIsCandidate
from .abstract_is_examiner import AbstractIsExaminer
from .basenode import BaseNode
from .custom_db_fields import ShortNameField, LongNameField
from devilry.devilry_account.models import User, PeriodPermissionGroup
from .model_utils import Etag
from .subject import Subject


class PeriodQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.PeriodManager`.
    """

    def filter_user_is_relatedstudent(self, user):
        """
        Filter only periods where the given user is relatedstudent.
        """
        queryset = self.filter(relatedstudent__user=user)
        return queryset.distinct()

    def filter_active(self):
        """
        Filter only active periods.
        """
        now = timezone.now()
        return self.filter(start_time__lt=now, end_time__gt=now)

    def filter_has_started(self):
        """
        Filter only started periods.
        """
        now = timezone.now()
        return self.filter(start_time__lt=now)

    def filter_user_is_admin(self, user):
        """
        Filter the queryset to only include :class:`.Period` objects where the
        given ``user`` is in a :class:`.devilry.devilry_account.models.SubjectPermissionGroup`
        or in a :class:`.devilry.devilry_account.models.PeriodPermissionGroup`.

        Args:
            user: A User object.
        """
        if user.is_superuser:
            return self.all()
        else:
            subjectids_where_is_admin_queryset = Subject.objects\
                .filter_user_is_admin(user=user)\
                .values_list('id', flat=True)
            periodids_where_is_admin_queryset = PeriodPermissionGroup.objects \
                .filter(models.Q(permissiongroup__users=user))\
                .values_list('period_id', flat=True)
            return self.filter(
                models.Q(id__in=periodids_where_is_admin_queryset) |
                models.Q(parentnode_id__in=subjectids_where_is_admin_queryset)
            )

    def extra_annotate_with_user_qualifies_for_final_exam(self, user):
        """
        Annotate the queryset with ``user_qualifies_for_final_exam`` - ``True`` if the user
        qualifies for final exams, ``False`` if the user does not qualify for final exams,
        and ``None`` if qualifies for final exam has not been determined yet.
        """
        from devilry.devilry_qualifiesforexam.models import Status
        return self.extra(
                select={
                    'user_qualifies_for_final_exam': """
                        SELECT
                            CASE
                                WHEN
                                    devilry_qualifiesforexam_status.status = %s
                                THEN
                                    NULL
                                ELSE
                                    devilry_qualifiesforexam_qualifiesforfinalexam.qualifies
                            END
                        FROM devilry_qualifiesforexam_status
                        INNER JOIN core_relatedstudent ON
                          core_relatedstudent.period_id = core_period.id
                          AND
                          core_relatedstudent.user_id = %s
                        LEFT JOIN devilry_qualifiesforexam_qualifiesforfinalexam ON
                          devilry_qualifiesforexam_qualifiesforfinalexam.status_id = devilry_qualifiesforexam_status.id
                          AND
                          devilry_qualifiesforexam_qualifiesforfinalexam.relatedstudent_id = core_relatedstudent.id
                        WHERE
                          core_period.id = devilry_qualifiesforexam_status.period_id
                        ORDER BY devilry_qualifiesforexam_status.createtime DESC
                        LIMIT 1
                """
                },
                select_params=[
                    Status.NOTREADY,
                    user.id,
                ]
        )

    def extra_annotate_with_assignmentcount_for_studentuser(self, user):
        """
        Annotate with ``assignmentcount_for_studentuser`` - the number of assignments
        within each Period in the queryset where the given ``user`` is candidate.

        Args:
            user: A User object.
        """
        return self.extra(
                select={
                    'assignmentcount_for_studentuser': """
                        SELECT
                            COUNT(core_assignment.id)
                        FROM core_assignment
                        LEFT OUTER JOIN core_assignmentgroup
                            ON (core_assignmentgroup.parentnode_id = core_assignment.id)
                        INNER JOIN core_candidate
                            ON (core_candidate.assignment_group_id = core_assignmentgroup.id)
                        INNER JOIN core_relatedstudent
                            ON (core_relatedstudent.id = core_candidate.relatedstudent_id)
                        WHERE
                            core_relatedstudent.user_id = %s
                            AND
                            core_assignment.parentnode_id = core_period.id
                    """
                },
                select_params=[
                    user.id,
                ]
        )


class Period(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate, Etag):
    """
    A Period represents a period of time, for example a half-year term
    at a university.


    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Subject`_.

    .. attribute:: start_time

        A django.db.models.DateTimeField_ representing the starting time of
        the period.

    .. attribute:: end_time

        A django.db.models.DateTimeField_ representing the ending time of
        the period.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        node.

    .. attribute:: assignments

        A Django RelatedManager of :class:`assignments <devilry.apps.core.models.Assignment>` for this period.

    .. attribute:: relatedexaminer_set

        A Django RelatedManager of :class:`RelatedExaminers <devilry.apps.core.models.RelatedExaminer>` for this period.

    .. attribute:: relatedstudent_set

        A Django RelatedManager of :class:`RelatedStudents <devilry.apps.core.models.RelatedStudent>` for this period.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    """
    objects = PeriodQuerySet.as_manager()

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']
        verbose_name = gettext_lazy('semester')
        verbose_name_plural = gettext_lazy('semesters')

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject, related_name='periods',
                                   verbose_name=gettext_lazy('Subject'),
                                   on_delete=models.CASCADE)
    start_time = models.DateTimeField(
        help_text=gettext_lazy('Start time and end time defines when the period is active.'),
        verbose_name=gettext_lazy('Start time'))
    end_time = models.DateTimeField(
        help_text=gettext_lazy('Start time and end time defines when the period is active.'),
        verbose_name=gettext_lazy('End time'))
    admins = models.ManyToManyField(User, blank=True)
    etag = models.DateTimeField(auto_now_add=True)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = timezone.now()
        q = Q(assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(end_time__gte=now)
        if not old:
            q &= ~Q(end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignments__assignmentgroups__candidates__student=user_obj)

    def clean(self, *args, **kwargs):
        """Validate the period.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if start_time is after end_time.
        """
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError(gettext_lazy('Start time must be before end time.'))
        super(Period, self).clean(*args, **kwargs)

    def is_active(self):
        """ Returns true if the period is active
        """
        now = timezone.now()
        return self.start_time < now < self.end_time

    @classmethod
    def q_is_active(self):
        """
        Get a ``django.db.models.Q`` object that matches all active periods (periods where start_time is
        in the past, and end_time is in the future).

        Example::

            activeperiods = Period.objects.filter(Period.q_is_active())
        """
        now = timezone.now()
        return Q(start_time__lt=now, end_time__gt=now)

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignments__assignmentgroups__examiners__user=user_obj)

    @classmethod
    def where_is_relatedstudent(cls, user_obj):
        return cls.objects.filter(cls.q_is_relatedstudent(user_obj)).distinct()

    @classmethod
    def q_is_relatedstudent(cls, user_obj):
        return Q(relatedstudent__user=user_obj)

    def is_empty(self):
        """
        Returns ``True`` if this Period does not contain any assignments.
        """
        return self.assignments.count() == 0

    @property
    def subject(self):
        """
        More readable alternative to ``self.parentnode``.
        """
        return self.parentnode

    def __str__(self):
        return self.get_path()


class PeriodApplicationKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific Period. """
    period = models.ForeignKey(Period, help_text="The period where this metadata belongs.", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('period', 'application', 'key')
        app_label = 'core'

    def __str__(self):
        return '{0}: {1}'.format(self.period, super(AbstractApplicationKeyValue, self))
