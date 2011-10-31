from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.db.models import Q

from datetime import datetime

from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from assignment_group import AssignmentGroup
from abstract_is_admin import AbstractIsAdmin

from node import Node


class Deadline(models.Model, AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate):
    """ A deadline on an `AssignmentGroup`_. A deadline contains zero or more
    `deliveries <Delivery>`_, the time of the deadline and an optional text.

    .. attribute:: assignment_group

        The `AssignmentGroup`_ where the deadline is registered.

    .. attribute:: deadline

        The deadline a DateTimeField.

    .. attribute:: text

        A optional deadline text.

    .. attribute:: deliveries

        A django ``RelatedManager`` that holds the `deliveries <Delivery>`_ on this group.

    .. attribute:: deliveries_available_before_deadline

        Should deliveries on this deadline be available to examiners before the
        deadline expires? This is set by students.

    .. attribute:: feedbacks_published

        If this boolean field is ``True``, the student can see all
        :class:`StaticFeedback` objects associated with this Deadline through a
        :class:`Delivery`. See also :attr:`Assignment.examiners_publish_feedbacks_directly`.

    """
    assignment_group = models.ForeignKey(AssignmentGroup,
            related_name='deadlines')
    deadline = models.DateTimeField(help_text=_('The time of the deadline.'))
    text = models.TextField(blank=True, null=True,
                            help_text=_('An optional text to show to students and examiners.'))
    deliveries_available_before_deadline = models.BooleanField(default=False,
                                                              help_text=_('Should deliveries on this deadline be available to examiners before the'
                                                                          'deadline expires? This is set by students.'))
    feedbacks_published = models.BooleanField(default=False,
                                              help_text=_('If this is ``True``, the student can see all '\
                                                          'StaticFeedbacks associated with this Deadline'))

    class Meta:
        app_label = 'core'
        verbose_name = _('Deadline')
        verbose_name_plural = _('Deadlines')
        ordering = ['-deadline']

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

    def save(self, *args, **kwargs):
        if self.id == None:
            self.assignment_group.is_open = True
            self.assignment_group.save()
        super(Deadline, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.deadline)

    #TODO delete this?
    #def is_old(self):
        #""" Return True if :attr:`deadline` expired. """
        #return self.deadline < datetime.now()

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignment_group__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

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
    def q_is_candidate(cls, user_obj):
        return Q(assignment_group__candidates__student=user_obj)

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignment_group__examiners__user=user_obj)
