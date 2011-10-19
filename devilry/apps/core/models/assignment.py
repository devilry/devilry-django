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

    .. attribute:: filenames
    
        A optional string of filenames separated by whitespace.

    .. attribute:: pointscale

        The points will be scaled down or up making the _this_
        number the maximum number of points. Defaults to 1.

    .. attribute:: autoscale
            
        If this field is True, the pointscale will automatically be set
        to the maximum number of points possible with the selected grade
        plugin.

    .. attribute:: must_pass
        
        Each student must get a passing grade on this assignment to get a
        passing grade on the period. Defaults to False.


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
    filenames = models.TextField(blank=True, null=True,
            verbose_name=_("Filenames"),
            help_text=_('Filenames separated by newline or space. If '
                'filenames are used, students will not be able to deliver '
                'files where the filename is not among the given filenames.'))
    must_pass = models.BooleanField(default=False,
            verbose_name=_("Must pass"),
            help_text=_('Each student must get a passing grade on this ' \
                'assignment to get a passing grade on the period.'))
    pointscale = models.PositiveIntegerField(default=1,
            verbose_name = _("Scaled maximum points"),
            help_text=_(
                'The points will be scaled down or up making the _this_ '
                'number the maximum number of points on this assignment. '
                'You use this to adjust how much an assignment counts '
                'towards the final grade (or towards passing the period). '
                'A typical example is when you have one assignment where '
                'it is possible to get 30 points, and one assignment '
                'where it is possible to get 1 point (like '
                'with the approved/notapproved plugin). If you want both '
                'to count for maximum 40 points, you set this field to 40 '
                'on both assignments.'))
    #maxpoints = models.PositiveIntegerField(default=0,
            #help_text=_('The maximum number of points possible without '\
                #'scaling.'))
    autoscale = models.BooleanField(default=True,
            verbose_name=_("Autoscale"),
            help_text=_('If this field is set, the pointscale will '\
                'automatically be set to the maximum number of points '\
                'possible with the selected grade plugin.'))
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

    def _update_scalepoints(self):
        for group in self.assignmentgroups.iterator():
            group.scaled_points = group._get_scaled_points()
            group.save()

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

    #TODO delete this?
    #def save(self, *args, **kwargs):
        #""" Save and recalculate the value of :attr:`maxpoints` and
        #:attr:`pointscale`. """
        #if self.autoscale:
            #self.pointscale = self.maxpoints
        #super(Assignment, self).save()
        #self._update_scalepoints()

    #TODO delete this?
    #def get_filenames(self):
        #""" Get the filenames as a list of strings. """
        #return self.filenames.split()

    #TODO delete this?
    #def validate_filenames(self, filenames):
        #""" Raise ValueError unless each filename in the iterable
        #``filenames`` is one of the filenames on this assignment. Nothing is
        #done if :attr:`filenames` is not set, or set to a empty string. """
        #if self.filenames:
            #valid = self.get_filenames()
            #for filename in filenames:
                #if not filename in valid:
                    #raise ValueError(_("Invalid filename: %(filename)s" %
                        #dict(filename=filename)))

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
