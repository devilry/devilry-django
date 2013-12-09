from django.core.exceptions import ValidationError
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
        NOTE: You should normally not use this directly, but rather use meth:`.query_successful_deliveries`.


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
    deadline = models.DateTimeField(help_text='The time of the deadline.')
    text = models.TextField(blank=True, null=True,
                            help_text='An optional text to show to students and examiners.')
    deliveries_available_before_deadline = models.BooleanField(default=False,
                                                              help_text='Should deliveries on this deadline be available to examiners before the'
                                                                          'deadline expires? This is set by students.')
    feedbacks_published = models.BooleanField(default=False,
                                              help_text='If this is ``True``, the student can see all '\
                                                          'StaticFeedbacks associated with this Deadline')

    class Meta:
        app_label = 'core'
        verbose_name = 'Deadline'
        verbose_name_plural = 'Deadlines'
        ordering = ['-deadline']


    def remove_microsec(self):
        self.deadline = self.deadline.replace(microsecond=0, tzinfo=None) # NOTE: We want this so a unique deadline is a deadline which matches with second-specition.

    def _clean_deadline(self):
        self.remove_microsec()
        qry = Q(deadline=self.deadline, assignment_group=self.assignment_group)
        if self.id:
            qry &= ~Q(id=self.id)
        deadlines = Deadline.objects.filter(qry)
        if deadlines.count() > 0:
            raise ValidationError('Can not have more than one deadline with the same date/time on a single group.')

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
                raise ValidationError('Deadline cannot be before publishing time.')

            if self.deadline > self.assignment_group.parentnode.parentnode.end_time:
                raise ValidationError(
                    "Deadline must be within it's period (%(period)s)."
                      % dict(period=unicode(self.assignment_group.parentnode.parentnode)))
            self._clean_deadline()
        super(Deadline, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.id == None:
            self.assignment_group.is_open = True
            self.assignment_group.save()
        super(Deadline, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.deadline)

    def __repr__(self):
        return 'Deadline(id={id}, deadline={deadline})'.format(**self.__dict__)

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


    def query_successful_deliveries(self):
        """
        Returns a django QuerySet that filters all the successful `deliveries
        <Delivery>`_ on this group.
        """
        return self.deliveries.filter(successful=True)

    def is_empty(self):
        """
        Returns ``True`` if this Deadline does not contain any deliveries.
        """
        return self.query_successful_deliveries().count() == 0

    def can_delete(self, user_obj):
        """
        Check if the given user is permitted to delete this object. A user is
        permitted to delete an Deadline if the user is superadmin, or if the user
        is admin on the assignment. Only superusers
        are allowed to delete deadlines with any deliveries.

        :return: ``True`` if the user is permitted to delete this object.
        """
        if self.id == None:
            return False
        if user_obj.is_superuser:
            return True
        if self.is_empty():
            return self.assignment_group.parentnode.is_admin(user_obj)
        else:
            return False


    def copy(self, newgroup):
        """
        Copy this deadline into ``newgroup``, including all deliveries and
        filemetas, with the actual file data.

        .. note:: Always run this is a transaction.

        .. warning::
            This does not autoset the latest feedback as active on the group.
            You need to handle that yourself after the copy.
        """
        deadlinecopy = Deadline(assignment_group=newgroup,
                                deadline=self.deadline,
                                text=self.text,
                                feedbacks_published=self.feedbacks_published)
        deadlinecopy.full_clean()
        deadlinecopy.save()
        for delivery in self.query_successful_deliveries():
            delivery.copy(deadlinecopy)
        return deadlinecopy
