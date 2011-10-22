from datetime import datetime

from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

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
       
    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    """
    class Meta:
        app_label = 'core'
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments',
                                   verbose_name=_('Period'))
    etag = models.DateTimeField(auto_now_add=True)
    publishing_time = models.DateTimeField(verbose_name=_("Publishing time"),
                                           help_text=_('The time when the assignment is to be published (visible to students and examiners).'))
    anonymous = models.BooleanField(default=False,
                                    verbose_name=_("Anonymous"),
                                    help_text=_('Specifies if this assignment is anonymous.'))
    students_can_see_points = models.BooleanField(default=True,
            verbose_name=_("Students can see points"))
    admins = models.ManyToManyField(User, blank=True,
            verbose_name=_("Administrators"))
    examiners_publish_feedbacks_directly = models.BooleanField(default=True,
                                                     verbose_name=_("Examiners publish directly?"),
                                                     help_text=_('Should feedbacks published by examiners be made '
                                                                 'avalable to the students immediately? If not, an '
                                                                 'administrator have to publish feedbacks '
                                                                 'manually.'))
    delivery_types = models.PositiveIntegerField(default=deliverytypes.ELECTRONIC,
                                                 choices=deliverytypes.as_choices_tuple(),
                                                 help_text='This option controls what types of deliveries this assignment accepts. See docs for Delivery for documentation of accepted values.')

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
        return Q(assignmentgroups__examiners=user_obj)

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
                    _("Publishing time must be within it's period (%(period)s)."
                      % dict(period=unicode(self.parentnode))))
