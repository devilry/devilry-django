from datetime import datetime

from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings

from basenode import BaseNode
from node import Node
from period import Period
from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from candidate import Candidate
from model_utils import *
from custom_db_fields import ShortNameField, LongNameField
from model_utils import Etag

import deliverytypes


class ExaminerAssignmentQuerySet(models.query.QuerySet):
    """
    Returns a queryset with all Assignments  where the given ``user`` is examiner.

    WARNING: You should normally not use this directly because it gives the
    examiner information from expired periods (which in most cases are not necessary
    to get). Use :meth:`.active` instead.
    """
    def filter_is_examiner(self, user):
        return self.filter(assignmentgroups__examiners__user=user).distinct()

    def filter_is_active(self):
        now = datetime.now()
        return self.filter(publishing_time__lt=now, parentnode__end_time__gt=now)


class ExaminerAssignmentManager(models.Manager):
    def get_queryset(self):
        return ExaminerAssignmentQuerySet(self.model, using=self._db)

    def filter_is_examiner(self, user):
        return self.get_queryset().filter_is_examiner(user)

    def filter_is_active(self, user):
        return self.get_queryset().filter_is_active()


class DefaultAssignmentManager(models.Manager):
    pass


class Assignment(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate, Etag):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Period`_.

    .. attribute:: publishing_time

        A django.db.models.DateTimeField_ representing the publishing time of
        the assignment.

    .. attribute:: anonymous

        A models.BooleanField specifying if the assignment should be
        anonymously for correcters.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        Node.

    .. attribute:: assignmentgroups

        A set of :class:`assignmentgroups <devilry.apps.core.models.AssignmentGroup>` for this assignment

    .. attribute:: examiners_publish_feedbacks_directly

       Should feedbacks published by examiners be made avalable to the
       students immediately? If not, an administrator have to publish
       feedbacks. See also :attr:`Deadline.feedbacks_published`.

    .. attribute:: scale_points_percent

        Percent to scale points on this assignment by for period overviews. The default is 100, which means no change to the points.

    .. attribute:: delivery_types

        An integer identifying the type of deliveries allowed. Possible values:

            0
                Electronic deliveries using Devilry
            1
                Non-electronic deliveries, or deliveries made through another
                electronic system.
            2
                An alias/link to a delivery made in another Period.

    .. attribute:: deadline_handling

        An integer identifying how deadlines are handled.

            0
                Soft deadlines. Deliveries can be added until groups are closed.
            1
                Hard deadlines. Deliveries can not be added after the deadline
                has expired.

    .. attribute:: etag

        A DateTimeField containing the etag for this object.

    .. attribute:: first_deadline

        A DateTimeField containing an optional first deadline for this
        assignment. This is metadata that the UI can use where it is
        natural.
    """
    objects = DefaultAssignmentManager()
    examiner_objects = ExaminerAssignmentManager()

    DEADLINEHANDLING_SOFT = 0
    DEADLINEHANDLING_HARD = 1

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments',
                                   verbose_name='Period')
    etag = models.DateTimeField(auto_now_add=True)
    publishing_time = models.DateTimeField(verbose_name="Publishing time",
                                           help_text='The time when the assignment is to be published (visible to students and examiners).')
    anonymous = models.BooleanField(default=False,
                                    verbose_name="Anonymous",
                                    help_text='Specifies if this assignment is anonymous.')
    students_can_see_points = models.BooleanField(default=True,
            verbose_name="Students can see points")
    admins = models.ManyToManyField(User, blank=True,
            verbose_name="Administrators")
    examiners_publish_feedbacks_directly = models.BooleanField(default=True,
                                                     verbose_name="Examiners publish directly?",
                                                     help_text=('Should feedbacks published by examiners be made '
                                                                'avalable to the students immediately? If not, an '
                                                                'administrator have to publish feedbacks '
                                                                'manually.'))
    delivery_types = models.PositiveIntegerField(default=deliverytypes.ELECTRONIC,
                                                 choices=deliverytypes.as_choices_tuple(),
                                                 help_text='This option controls what types of deliveries this assignment accepts. See the Delivery documentation for more info.')
    deadline_handling = models.PositiveIntegerField(default=settings.DEFAULT_DEADLINE_HANDLING_METHOD,
                                                    help_text='This option controls how devilry handles deadlines. 0=Soft, 1=Hard. See the Delivery documentation for more info.')
    scale_points_percent = models.PositiveIntegerField(default=100,
                                                       help_text='Percent to scale points on this assignment by for period overviews. The default is 100, which means no change to the points.')
    first_deadline = models.DateTimeField(blank=True, null=True)


    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(publishing_time__lt=now)
        if not active:
            q &= ~Q(parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignmentgroups__candidates__student=user_obj)

    def save(self, *args, **kwargs):
        if self.pk:
            # Only when assignment already exists in the database
            self.update_candidates_identifer()
        super(Assignment, self).save(*args, **kwargs)

    def update_candidates_identifer(self):
        """ If the anonymous flag is changed, update the identifer on all
        the candidates on this assignment.
        """
        # Get current value stored in the db
        db_assignment = Assignment.objects.get(id=self.id)
        # No change, so return
        if self.anonymous == db_assignment.anonymous:
            return
        # Get all candidates on assignmentgroups for this assignment
        candidates = Candidate.objects.filter(Q(assignment_group__parentnode__id=self.id))
        for cand in candidates: 
            #cand.update_identifier(self.anonymous)
            cand.save(anonymous=self.anonymous)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignmentgroups__examiners__user=user_obj)

    def _clean_first_deadline(self):
        self.first_deadline = self.first_deadline.replace(microsecond=0, tzinfo=None) # NOTE: We want this so a unique deadline is a deadline which matches with second-specition.
        datetimeformat = '%Y-%m-%d %H:%M'
        if self.first_deadline < self.publishing_time:
            msg = _('Submission date can not be before the publishing time ({publishing_time}) of the assignment.')
            raise ValidationError(msg.format(publishing_time = self.publishing_time.strftime(datetimeformat)))
        if self.first_deadline > self.parentnode.end_time:
            msg = _("Submission date must be within it's {period_term} ({start_time} - {end_time}).")
            raise ValidationError(msg.format(period_term=_('period'),
                                             start_time=self.parentnode.start_time.strftime(datetimeformat),
                                             end_time=self.parentnode.end_time.strftime(datetimeformat)))

    def clean(self, *args, **kwargs):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if ``publishing_time`` is not between
        :attr:`Period.start_time` and ``Period.end_time``.
        """
        super(Assignment, self).clean(*args, **kwargs)
        if self.publishing_time != None and self.parentnode_id != None:
            if self.publishing_time < self.parentnode.start_time  or \
                    self.publishing_time > self.parentnode.end_time:
                raise ValidationError(
                      _("The publishing time, {publishing_time}, is invalid. "
                        "It must be within it's period, {period}, "
                        "which lasts from {start_time} to {end_time}").format(publishing_time = self.publishing_time,
                                                                              period=unicode(self.parentnode),
                                                                              end_time=self.parentnode.end_time,
                                                                              start_time=self.parentnode.start_time))
        if self.first_deadline:
            self._clean_first_deadline()


    def is_empty(self):
        """
        Returns ``True`` if this Assignment does not contain any deliveries.
        """
        from .delivery import Delivery
        return Delivery.objects.filter(deadline__assignment_group__parentnode=self).count() == 0


    def is_active(self):
        """
        Returns ``True`` if this assignment is published, and the period has not ended yet.
        """
        now = datetime.now()
        return self.publishing_time < now and self.parentnode.end_time > now
