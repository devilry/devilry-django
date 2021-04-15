from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Max
from django.utils import timezone
from django.utils.translation import gettext_lazy

from . import deliverytypes
from .deadline import Deadline
from .filemeta import FileMeta
from . import AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate


class DeliveryQuerySet(models.QuerySet):
    """
    Returns a queryset with all Deliveries where the given ``user`` is examiner.
    """

    def filter_is_examiner(self, user):
        return self.filter(deadline__assignment_group__examiners__relateduser__user=user).distinct()

    def filter_is_candidate(self, user):
        return self.filter(deadline__assignment_group__candidates__relatedstudent__user=user).distinct()

    def filter_is_active(self):
        now = timezone.now()
        return self.filter(
            deadline__assignment_group__parentnode__publishing_time__lt=now,
            deadline__assignment_group__parentnode__parentnode__start_time__lt=now,
            deadline__assignment_group__parentnode__parentnode__end_time__gt=now).distinct()

    def filter_examiner_has_access(self, user):
        return self.filter_is_active().filter_is_examiner(user)


class DeliveryManager(models.Manager):
    def get_queryset(self):
        return DeliveryQuerySet(self.model, using=self._db)

    def filter_is_candidate(self, user):
        return self.get_queryset().filter_is_candidate(user)

    def filter_is_examiner(self, user):
        """
        Returns a queryset with all Deliveries where the given ``user`` is examiner.

        WARNING: You should normally not use this alone because it gives the
        examiner information from expired periods (which they are not supposed
        to get). Use :meth:`.filter_examiner_has_access` instead.
        """
        return self.get_queryset().filter_is_examiner(user)

    def filter_is_active(self):
        """
        Returns a queryset with all Deliveries on active Assignments.
        """
        return self.get_queryset().filter_is_active()

    def filter_examiner_has_access(self, user):
        """
        Returns a queryset with all Deliveries on active Assignments
        where the given ``user`` is examiner.

        NOTE: This returns all groups that the given ``user`` has examiner-rights for.
        """
        return self.get_queryset().filter_examiner_has_access(user)


class Delivery(models.Model, AbstractIsAdmin, AbstractIsCandidate, AbstractIsExaminer):
    """ A class representing a given delivery from an `AssignmentGroup`_.

    How to create a delivery::

        deadline = Deadline.objects.get(....)
        candidate = Candidate.objects.get(....)
        delivery = Delivery(
            deadline=deadline,
            delivered_by=candidate)
        delivery.set_number()
        delivery.full_clean()
        delivery.save()

    .. attribute:: time_of_delivery

        A django.db.models.DateTimeField_ that holds the date and time the
        Delivery was uploaded.

    .. attribute:: deadline

       A django.db.models.ForeignKey_ pointing to the `Deadline`_ for this Delivery.

    .. attribute:: number

        A django.db.models.fields.PositiveIntegerField with the delivery-number
        within this assignment-group. This number is automatically
        incremented within each assignmentgroup, starting from 1. Must be
        unique within the assignment-group. Automatic incrementation is used
        if number is None when calling :meth:`save`.

    .. attribute:: delivered_by

        A django.db.models.ForeignKey_ pointing to the user that uploaded
        the Delivery

    .. attribute:: successful

        A django.db.models.BooleanField_ telling whether or not the Delivery
        was successfully uploaded.

    .. attribute:: after_deadline

        A django.db.models.BooleanField_ telling whether or not the Delivery
        was delived after deadline..

    .. attribute:: filemetas

        A set of :class:`filemetas <devilry.apps.core.models.FileMeta>` for this delivery.

    .. attribute:: feedbacks

       A set of :class:`feedbacks <devilry.apps.core.models.StaticFeedback>` on this delivery.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    .. attribute:: copy_of

        Link to a delivery that this delivery is a copy of. This is set by :meth:`.Delivery.copy`.

    .. attribute:: last_feedback

       The last `StaticFeedback`_ on this delivery. This is updated each time a feedback is added.

    .. attribute:: copy_of

        If this delivery is a copy of another delivery, this ForeignKey points to that other delivery.

    .. attribute:: copies

        The reverse of ``copy_of`` - a queryset that returns all copies of this delivery.
    """
    # DELIVERY_NOT_CORRECTED = 0
    # DELIVERY_CORRECTED = 1
    objects = DeliveryManager()

    delivery_type = models.PositiveIntegerField(
        default=deliverytypes.ELECTRONIC,
        verbose_name="Type of delivery",
        help_text='0: Electronic delivery, 1: Non-electronic delivery, 2: Alias delivery. Default: 0.')
    time_of_delivery = models.DateTimeField(
        verbose_name=gettext_lazy('Time of delivery'),
        help_text='Holds the date and time the Delivery was uploaded.',
        default=timezone.now)
    deadline = models.ForeignKey(
        Deadline, related_name='deliveries',
        verbose_name=gettext_lazy('Deadline'), on_delete=models.CASCADE)
    number = models.PositiveIntegerField(
        help_text='The delivery-number within this assignment-group. This number is automatically '
                  'incremented within each AssignmentGroup, starting from 1. Always '
                  'unique within the assignment-group.')

    # Fields set by user
    successful = models.BooleanField(blank=True, default=True,
                                     help_text='Has the delivery and all its files been uploaded successfully?')
    delivered_by = models.ForeignKey(
        "Candidate", blank=True, null=True,
        on_delete=models.SET_NULL,
        help_text='The candidate that delivered this delivery. If this is None, '
                  'the delivery was made by an administrator for a student.')

    # Only used when this is aliasing an earlier delivery, delivery_type == ALIAS
    alias_delivery = models.ForeignKey("Delivery", blank=True, null=True,
                                       on_delete=models.SET_NULL,
                                       help_text='Links to another delivery. Used when delivery_type is Alias.')

    copy_of = models.ForeignKey(
        "Delivery", blank=True, null=True,
        related_name='copies',
        on_delete=models.SET_NULL,
        help_text='Link to a delivery that this delivery is a copy of. This is set by the copy-method.')
    last_feedback = models.OneToOneField("StaticFeedback", blank=True, null=True,
                                         related_name='latest_feedback_for_delivery', on_delete=models.CASCADE)

    def _delivered_too_late(self):
        """ Compares the deadline and time of delivery.
        If time_of_delivery is greater than the deadline, return True.
        """
        return self.time_of_delivery > self.deadline.deadline

    after_deadline = property(_delivered_too_late)

    class Meta:
        app_label = 'core'
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-time_of_delivery']
        # unique_together = ('assignment_group', 'number')

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching Deliveries where
        the given student is candidate.
        """
        return Q(successful=True) & Q(deadline__assignment_group__candidates__student=user_obj)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = timezone.now()
        q = Q(deadline__assignment_group__parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(deadline__assignment_group__parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(deadline__assignment_group__parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(successful=True) & Q(deadline__assignment_group__examiners__user=user_obj)

    @property
    def is_last_delivery(self):
        """
        Returns ``True`` if this is the last delivery for this AssignmentGroup.
        """
        try:
            last_delivery = Delivery.objects \
                .filter(deadline__assignment_group_id=self.deadline.assignment_group_id) \
                .order_by('-time_of_delivery').first()
            return last_delivery == self
        except Delivery.DoesNotExist:
            return False

    @property
    def assignment_group(self):
        """
        Shortcut for ``self.deadline.assignment_group.assignment``.
        """
        return self.deadline.assignment_group

    @property
    def assignment(self):
        """
        Shortcut for ``self.deadline.assignment_group.assignment``.
        """
        return self.assignment_group.assignment

    def add_file(self, filename, iterable_data):
        """ Add a file to the delivery.

        :param filename:
            A filename as defined in :class:`FileMeta`.
        :param iterable_data:
            A iterable yielding data that can be written to file using the
            write() method of a storage backend (byte strings).
        """
        filemeta = FileMeta()
        filemeta.delivery = self
        filemeta.filename = filename
        filemeta.size = 0
        filemeta.save()
        f = FileMeta.deliverystore.write_open(filemeta)
        filemeta.save()
        for data in iterable_data:
            f.write(data.decode('utf-8'))
            filemeta.size += len(data)
        f.close()
        filemeta.save()
        return filemeta

    def set_number(self):
        m = Delivery.objects.filter(deadline__assignment_group=self.deadline.assignment_group).aggregate(Max('number'))
        self.number = (m['number__max'] or 0) + 1

    def set_time_of_delivery_to_now(self):
        self.time_of_delivery = timezone.now().replace(microsecond=0, tzinfo=None)

    def clean(self):
        """ Validate the delivery. """
        if self.delivery_type == deliverytypes.ALIAS:
            if not self.alias_delivery and not self.feedbacks.exists():
                raise ValidationError('A Delivery with delivery_type=ALIAS must have an alias_delivery or feedback.')
        super(Delivery, self).clean()

    def __str__(self):
        return ('Delivery(id={id}, number={number}, group={group}, '
                'time_of_delivery={time_of_delivery})').format(id=self.id,
                                                                group=self.deadline.assignment_group,
                                                                number=self.number,
                                                                time_of_delivery=self.time_of_delivery.isoformat())

    def copy(self, newdeadline):
        """
        Copy this delivery, including all FileMeta's and their files, and all
        feedbacks into ``newdeadline``. Sets the ``copy_of`` attribute of the
        created delivery.

        .. note:: Always run this in a transaction.

        .. warning::
            This does not autoset the latest feedback as ``feedback`` or
            the ``last_delivery`` on the group.
            You need to handle that yourself after the copy.

        :return: The newly created, cleaned and saved delivery.
        """
        deliverycopy = Delivery(deadline=newdeadline,
                                delivery_type=self.delivery_type,
                                number=self.number,
                                successful=self.successful,
                                time_of_delivery=self.time_of_delivery,
                                delivered_by=self.delivered_by,
                                alias_delivery=self.alias_delivery,
                                last_feedback=None,
                                copy_of=self)

        def save_deliverycopy():
            deliverycopy.save()

        deliverycopy.full_clean()
        save_deliverycopy()
        for filemeta in self.filemetas.all():
            filemeta.copy(deliverycopy)
        for index, staticfeedback in enumerate(self.feedbacks.order_by('-save_timestamp')):
            staticfeedbackcopy = staticfeedback.copy(deliverycopy)
            if index == 0:
                deliverycopy.last_feedback = staticfeedbackcopy
                save_deliverycopy()
        return deliverycopy

    def is_electronic(self):
        """
        Returns ``True`` if :attr:`Delivery.delivery_type` is ``0`` (electric).
        """
        return self.delivery_type == deliverytypes.ELECTRONIC

    def is_nonelectronic(self):
        """
        Returns ``True`` if :attr:`Delivery.delivery_type` is ``1`` (non-electric).
        """
        return self.delivery_type == deliverytypes.NON_ELECTRONIC
