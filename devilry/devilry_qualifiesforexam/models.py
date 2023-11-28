# -*- coding: utf-8 -*-


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.core.exceptions import ValidationError

from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import Period
from devilry.devilry_account.models import User


class DeadlineTag(models.Model):
    timestamp = models.DateTimeField()
    tag = models.CharField(max_length=30, null=True, blank=True)


class PeriodTag(models.Model):
    period = models.OneToOneField(Period, primary_key=True, on_delete=models.CASCADE)
    deadlinetag = models.ForeignKey(DeadlineTag, on_delete=models.CASCADE)


class StatusQuerySet(models.QuerySet):
    """
    QuerySet-manager for :class:`~.Status`.
    """

    def _get_qualifiesforexam_queryset(self):
        """
        Get :class:`~.QualifiesForFinalExam` and fetch the
        related :class:`~.devilry.apps.core.models.RelatedStudent` with select_related.

        Returns:
            QuerySet of :class:`~.QualifiesForFinalExam` objects.
        """
        return QualifiesForFinalExam.objects\
            .select_related('relatedstudent')

    def get_last_status_in_period(self, period, prefetch_relations=True):
        """
        Get the last :class:`~.Status` for the period.

        Prefetches all :class:`~.QualifiesForFinalExam` for the :class:`~.Status` objects and
        selects the last status.

        Args:
            period: current period.
            prefetch_relations: Prefetches the period for the Status and the
                related :class:`~.QualifiesForFinalExam`.

        Returns:
            The latest :class:`~.Status`.
        """
        if prefetch_relations:
            latest_status = period.qualifiedforexams_status\
                .select_related('period')\
                .prefetch_related(
                    models.Prefetch(
                            'students',
                            queryset=self._get_qualifiesforexam_queryset()))\
                .order_by('-createtime').first()
        else:
            latest_status = period.qualifiedforexams_status.order_by('-createtime').first()
        return latest_status


class Status(models.Model):

    #: Sets :class:`~.StatusQuerySet` as manager for model.
    objects = StatusQuerySet.as_manager()

    #: The list of qualified students are ready for export.
    #: Usually this means that all students have received a feedback
    #: on their assignments.
    #:
    #: This should be the default when creating a new Status for a Period.
    READY = 'ready'

    #: Most students are ready for export.
    #: Almost all students have received a feedback on their assignments.
    #: TODO: Legacy, to be removed.
    ALMOSTREADY = 'almostready'

    #: Students have pending feedbacks.
    #: This should be used when students students are awaiting feedback on assignments.
    #: Typically the status is ``not ready`` if no students(or just a few) have received
    #: a feedback on the last assignment.
    NOTREADY = 'notready'

    #: Choice list for status on the qualification list.
    STATUS_CHOICES = [
        (READY, gettext_lazy('Ready for export')),
        (ALMOSTREADY, gettext_lazy('Most students are ready for export')),
        (NOTREADY, gettext_lazy('Not ready for export (retracted)')),
    ]

    #: The status of the qualification list.
    #: Note: The statuses does not represent any final state in the system, and
    #: the admin can use these statuses as they see fit
    status = models.CharField(
            max_length=30,
            blank=False,
            choices=STATUS_CHOICES)

    #: Period the qualifications are for.
    period = models.ForeignKey(Period, related_name='qualifiedforexams_status', on_delete=models.CASCADE)

    #: Status created datetime. This is changed if the list updated.
    createtime = models.DateTimeField(default=timezone.now)

    #: Message provided with the qualification list of why
    #: it was retracted.
    message = models.TextField(blank=True, default='')

    #: The user that created the qualification list(an admin).
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #: The plugin used.
    plugin = models.CharField(max_length=500, null=True, blank=True)
    
    #: Plugin related data.
    plugin_data = models.JSONField(null=True, blank=True)

    #: The datetime when the list was exported.
    #: If this is null, this is considered a draft for preview before it's saved.
    exported_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-createtime']
        verbose_name = gettext_lazy('Qualified for final exam status')
        verbose_name_plural = gettext_lazy('Qualified for final exam statuses')

    def get_status_text(self):
        return self.status

    def clean(self):
        if self.status == 'notready' and not self.message:
            raise ValidationError('Message can not be empty when status is ``notready``.')
        if self.status != 'notready':
            if not self.plugin and not self.message:
                raise ValidationError('A ``message`` is required when no ``plugin`` is specified. '
                                      'The message should explain why a plugin is not used.')
        if self.status == 'notready':
            if self.plugin:
                raise ValidationError('``plugin`` is not allowed when status is ``notready``.')

    def get_qualified_students(self):
        return self.students.filter(qualifies=True)

    def __str__(self):
        return 'Status(period={period}, id={id}, status={status})'.format(
            id=self.id, status=self.period, period=self.period)


class QualifiesForFinalExam(models.Model):
    #: The related :obj:`~.devilry.apps.core.RelatedStudent` the qualification is for.
    relatedstudent = models.ForeignKey(RelatedStudent, on_delete=models.CASCADE)

    #: The related :obj:`~.Status` for this student.
    status = models.ForeignKey(Status, related_name='students', on_delete=models.CASCADE)

    #: ``True`` if the student qualifies for the exam, else ``False``.
    qualifies = models.BooleanField(null=True)

    class Meta:
        unique_together = ('relatedstudent', 'status')

    def clean(self):
        if self.qualifies is None and self.status.status != 'almostready':
            raise ValidationError('Only the ``almostready`` status allows marking students as not ready for export.')
        if self.status.status == 'notready':
            raise ValidationError('Status ``notready`` does not allow marking qualified students.')

    def __str__(self):
        return '{}-{}-{}'.format(self.relatedstudent, self.status, self.qualifies)

    def smart_delete(self):
        DeletedQualifiesForFinalExam.objects.create(
            relatedstudent=self.relatedstudent,
            status=self.status,
            qualifies=self.qualifies
        )
        self.delete()


class DeletedQualifiesForFinalExam(models.Model):
    #: The related :obj:`~.devilry.apps.core.RelatedStudent` the qualification is for.
    relatedstudent = models.ForeignKey(RelatedStudent, on_delete=models.CASCADE)

    #: The related :obj:`~.Status` for this student.
    status = models.ForeignKey(Status, related_name='+', on_delete=models.CASCADE)

    #: ``True`` if the student qualifies for the exam, else ``False``.
    qualifies = models.BooleanField(null=True)
