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

        A set of :class:`assignments <devilry.apps.core.models.Assignment>` for this period.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    .. attribute:: relatedstudents

        A django.db.models.ForeignKey_ that points to the related students for this period.
   
    .. attribute:: relatedexaminers

        A django.db.models.ForeignKey_ that points to the related examiners for this period.
   
    """
    class Meta:
        app_label = 'core'
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject, related_name='periods',
                                   verbose_name = _('Subject'))
    start_time = models.DateTimeField(
            help_text=_(
                'Start time and end time defines when the period is active.'))
    end_time = models.DateTimeField(
            help_text=_(
                'Start time and end time defines when the period is active.'))
    admins = models.ManyToManyField(User, blank=True)
    minimum_points = models.PositiveIntegerField(default=0,
            help_text=_('Students must get at least this many points to '\
                    'pass the period.'))
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

    #TODO delete this?
    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignments__assignmentgroups__candidates__student=user_obj)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    #TODO delete this?
    #@classmethod
    #def not_ended_where_is_admin(cls, user_obj):
        #""" Returns a QuerySet matching all Periods where the given user is
        #admin and end_time is in the future.
        
        #:param user_obj: A django.contrib.auth.models.User_ object.
        #:rtype: QuerySet
        #"""
        #return cls.where_is_admin(user_obj).filter(end_time__gt=datetime.now())

    #TODO delete this?
    #@classmethod
    #def not_ended_where_is_admin_or_superadmin(cls, user_obj):
        #""" Returns a QuerySet matching all Periods where the given user is
        #admin or superadmin and end_time is in the future.
        
        #:param user_obj: A django.contrib.auth.models.User_ object.
        #:rtype: QuerySet
        #"""
        #if user_obj.is_superuser:
            #return cls.objects.filter(end_time__gt=datetime.now())
        #else:
            #return cls.not_ended_where_is_admin(user_obj)

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

    #TODO delete this?
    def is_active(self):
        """ Returns true if the period is active
        """
        now = datetime.now()
        return self.start_time < now and self.end_time > now

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignments__assignmentgroups__examiners__user=user_obj)



class PeriodApplicationKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific Period. """
    period = models.ForeignKey(Period)

    class Meta:
        unique_together = ('period', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(period__admins=user_obj) | \
                Q(period__parentnode__admins=user_obj) | \
                Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return '{0}: {1}'.format(self.period, super(RelatedStudentKeyValue, self).__unicode__())
