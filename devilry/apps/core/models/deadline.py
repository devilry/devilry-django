from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.db.models import Q

from datetime import datetime

from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from assignment_group import AssignmentGroup

from node import Node


class Deadline(models.Model, AbstractIsExaminer, AbstractIsCandidate):
    """
    .. attribute:: assignment_group

        The assignment group where the deadline is registered.

    .. attribute:: deadline

        The deadline a DateTimeField.

    .. attribute:: text

        A optional deadline text.

   .. attribute:: deliveries

        A django ``RelatedManager`` that holds the :class:`deliveries
        <Delivery>` on this group.

   .. attribute:: status

        The status of this deadline. The data can be deduces from other data in the database, but
        since this requires complex queries, we store it as a integer
        instead, with the following values:

            0. No deliveries
            1. Has deliveries
            2. Corrected, not published
            3. Corrected and published

    .. attribute:: feedbacks_published

        If this boolean field is ``True``, the student can see all
        :class:`StaticFeedback` objects associated with this Deadline through a
        :class:`Delivery`. See also :attr:`Assignment.examiners_publish_feedbacks_directly`.
    """
    status = models.PositiveIntegerField(
            default = 0,
            choices = enumerate(AssignmentGroup.status_mapping),
            verbose_name = _('Status'))
    assignment_group = models.ForeignKey(AssignmentGroup,
            related_name='deadlines') 
    deadline = models.DateTimeField()
    text = models.TextField(blank=True, null=True)
    is_head = models.BooleanField(default=False)
    deliveries_available_before_deadline = models.BooleanField(default=False)
    feedbacks_published = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        verbose_name = _('Deadline')
        verbose_name_plural = _('Deadlines')
        ordering = ['-deadline']

    def _get_status_from_qry(self):
        """Get status for active deadline"""
        if self.deliveries.all().count == 0:
            return AssignmentGroup.NO_DELIVERIES
        else:
            deliveries_with_feedback = [delivery for delivery in self.deliveries.all() \
                                        if delivery.feedbacks.all().count() > 0]
            if deliveries_with_feedback:
                if self.feedbacks_published:
                    return AssignmentGroup.CORRECTED_AND_PUBLISHED
                else:
                    return AssignmentGroup.CORRECTED_NOT_PUBLISHED
            else:
                return AssignmentGroup.HAS_DELIVERIES

    def _update_status(self):
        """ Query for the correct status, and set :attr:`status`. """
        self.status = self._get_status_from_qry()
    
    def clean(self, *args, **kwargs):
        """Validate the deadline.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - ``deadline`` is before ``Assignment.publishing_time``. 
            - ``deadline`` is not before ``Period.end_time``.
        """
        if self.deadline != None:
            if self.deadline < self.assignment_group.parentnode.publishing_time:
                raise ValidationError(_('Deadline cannot be before publishing time.'))
            
            if self.deadline > self.assignment_group.parentnode.parentnode.end_time:
                raise ValidationError(
                    _("Deadline must be within it's period (%(period)s)."
                      % dict(period=unicode(self.assignment_group.parentnode.parentnode))))
        super(Deadline, self).clean(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.deadline)

    #TODO delete this?
    #def is_old(self):
        #""" Return True if :attr:`deadline` expired. """
        #return self.deadline < datetime.now()

    #TODO delete this?
    #def delete(self, *args, **kwargs):
        #""" Prevent deletion if this is the head deadline """
        #if self.is_head:
            #raise PermissionDenied()
        #super(Deadline, self).delete(*args, **kwargs)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignment_group__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def where_is_admin_or_superadmin(cls, user_obj):
        return cls.objects.filter(cls.q_is_admin(user_obj))
    
    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(assignment_group__parentnode__publishing_time__lt = now)
        if not active:
            q &= ~Q(assignment_group__parentnode__parentnode__end_time__gte = now)
        if not old:
            q &= ~Q(assignment_group__parentnode__parentnode__end_time__lt = now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignment_group__examiners=user_obj)
