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

class Period(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
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

        A set of assignments for this period 
    """

    class Meta:
        app_label = 'core'
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject, related_name='periods')
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
        return Q(assignmentgroups__candidates__student=user_obj)

    #TODO delete this?
    #def student_sum_scaled_points(self, user):
        #groups = AssignmentGroup.published_where_is_candidate(user).filter(
                #parentnode__parentnode=self)
        #return groups.aggregate(models.Sum('scaled_points'))['scaled_points__sum']

    def student_passes_period(self, user):
        groups = AssignmentGroup.published_where_is_candidate(user).filter(
                parentnode__parentnode=self,
                is_passing_grade=False,
                parentnode__must_pass=True)
        if groups.count() > 0:
            return False
        totalpoints = self.student_sum_scaled_points(user)
        return totalpoints >= self.minimum_points

    #TODO delete this?
    #def get_must_pass_assignments(self):
        #return self.assignments.filter(must_pass=True)

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

    @classmethod
    def get_by_path(self, path):
        """ Get a Period by path.

        Raises :exc:`Period.DoesNotExist` if the query does not match.
        Raises :exc:`ValueError` if the path does not contain exactly two
        path-elements (uses :func:`splitpath`).
        
        :param path: The path to a Period, like ``'inf1100.spring09'``.
        :return: A Period-object.
        """
        subject, period = splitpath(path, expected_len=2)
        return Period.objects.get(
                parentnode__short_name=subject,
                short_name=period)

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
    #def is_active(self):
        #""" Returns true if the period is active
        #"""
        #now = datetime.now()
        #return self.start_time < now and self.end_time > now

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignments__assignmentgroups__examiners=user_obj)
