from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import models

from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from custom_db_fields import ShortNameField, LongNameField
from basenode import BaseNode
from node import Node
from subject import Subject
from model_utils import Etag
from abstract_is_admin import AbstractIsAdmin
from abstract_applicationkeyvalue import AbstractApplicationKeyValue


class PeriodQuerySet(models.query.QuerySet):
    """
    QuerySet for :class:`.PeriodManager`.
    """
    def filter_is_candidate_or_relatedstudent(self, user):
        """
        See :meth:`.PeriodManager.filter_is_candidate_or_relatedstudent`.
        """
        from devilry.apps.core.models import Candidate
        periods_where_is_candidate_queryset = Candidate.objects\
            .filter(student=user)\
            .values_list('assignment_group__parentnode__parentnode_id', flat=True)\
            .distinct()
        queryset = self.filter(
            Q(relatedstudent__user=user) |
            Q(id__in=periods_where_is_candidate_queryset)
        )
        return queryset.distinct()

    def filter_active(self):
        """
        See :meth:`.PeriodManager.filter_active`.
        """
        now = datetime.now()
        return self.filter(start_time__lt=now, end_time__gt=now)

    def annotate_with_user_qualifies_for_final_exam(self, user):
        """
        See :meth:`.PeriodManager.annotate_with_user_qualifies_for_final_exam`.
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


class PeriodManager(models.Manager):
    """
    Manager for :class:`.Period`.
    """

    def get_queryset(self):
        return PeriodQuerySet(self.model, using=self._db)

    def filter_active(self):
        """
        Filter only active periods.
        """
        return self.get_queryset().filter_active()

    def filter_is_candidate_or_relatedstudent(self, user):
        """
        Filter only periods where the given ``user`` is one of:

        - :class:`devilry.apps.core.models.RelatedUser`
        - :class:`devilry.apps.core.models.Candidate`
        """
        return self.get_queryset().filter_is_candidate_or_relatedstudent(user)

    def annotate_with_user_qualifies_for_final_exam(self, user):
        """
        Annotate the queryset with the
        :obj:`devilry.devilry_qualifiesforexam.models.QualifiesForFinalExam.qualifies`
        value for the given ``user``.

        Should be used with :meth:`.filter_is_candidate_or_relatedstudent`.
        """
        return self.get_queryset().annotate_with_user_qualifies_for_final_exam(user)


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
    objects = PeriodManager()

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject, related_name='periods',
                                   verbose_name='Subject')
    start_time = models.DateTimeField(
        help_text='Start time and end time defines when the period is active.')
    end_time = models.DateTimeField(
        help_text='Start time and end time defines when the period is active.')
    admins = models.ManyToManyField(User, blank=True)
    etag = models.DateTimeField(auto_now_add=True)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(end_time__gte=now)
        if not old:
            q &= ~Q(end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignments__assignmentgroups__candidates__student=user_obj)

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(admins=user_obj) | \
            Q(parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def clean(self, *args, **kwargs):
        """Validate the period.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if start_time is after end_time.
        """
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError(_('Start time must be before end time.'))
        super(Period, self).clean(*args, **kwargs)

    def is_active(self):
        """ Returns true if the period is active
        """
        now = datetime.now()
        return self.start_time < now < self.end_time

    @classmethod
    def q_is_active(self):
        """
        Get a ``django.db.models.Q`` object that matches all active periods (periods where start_time is
        in the past, and end_time is in the future).

        Example::

            activeperiods = Period.objects.filter(Period.q_is_active())
        """
        now = datetime.now()
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


class PeriodApplicationKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific Period. """
    period = models.ForeignKey(Period, help_text="The period where this metadata belongs.")

    class Meta:
        unique_together = ('period', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(period__admins=user_obj) | \
            Q(period__parentnode__admins=user_obj) | \
            Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return '{0}: {1}'.format(self.period, super(AbstractApplicationKeyValue, self).__unicode__())
