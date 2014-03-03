from datetime import datetime

from django.utils.translation import ugettext as _
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
from model_utils import *
from model_utils import Etag
from abstract_is_admin import AbstractIsAdmin
from abstract_applicationkeyvalue import AbstractApplicationKeyValue





class PeriodQuerySet(models.query.QuerySet):
    pass


class PeriodManager(models.Manager):
    def get_queryset(self):
        return PeriodQuerySet(self.model, using=self._db)

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def all(self, *args, **kwargs):
        return self.get_queryset().all(*args, **kwargs)

    def create_many(self, subjects, **kwargs):
        """
        Create periods for the given subjects. ``kwargs`` is the same as for meth:`Period.__init__`.

        Should always run in a transaction to avoid creating periods for only
        some of the subjects in the queryset in case of errors.

        :param subjects: Iterable of :class:`devilry.apps.core.models.Subject`.

        Example::

            from datetime import datetime
            Period.objects.create_many(
                Subject.objects.filter(short_name__startswith="inf"),
                short_name='spring2014',
                start_time=datetime(2014, 1, 1),
                start_time=datetime(2014, 7, 1))
        """
        def create_period(subject):
            return Period(parentnode=subject, **kwargs)
        periods = map(create_period, subjects)
        self.bulk_create(periods)





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
        return Q(admins=user_obj) | \
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
        return self.start_time < now and self.end_time > now

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



class PeriodApplicationKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific Period. """
    period = models.ForeignKey(Period, help_text="The period where this metadata belongs.")

    class Meta:
        unique_together = ('period', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(period__admins=user_obj) | \
                Q(period__parentnode__admins=user_obj) | \
                Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return '{0}: {1}'.format(self.period, super(AbstractApplicationKeyValue, self).__unicode__())
