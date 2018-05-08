from django.db import models
from django.conf import settings
from django.utils import timezone

from devilry.apps.core.models import AssignmentGroup


class AbstractExaminerCandidateAssignmentGroupHistory(models.Model):
    """
    Abstract model that defines fields for logging insert/delete events of ``Examiner`` and ``Candidate`` objects
    on an ``AssignmentGroup``.
    """

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup` the
    #: user belonged/belongs to.
    #:
    #: The user belonged this group if the :obj:`.AbstractExaminerCandidateAssigmentGroupHistory.is_add` is ``False``.
    assignment_group = models.ForeignKey(
        to=AssignmentGroup,
        on_delete=models.CASCADE
    )

    #: The user that was related to the :obj:`AbstractExaminerCandidateAssigmentGroupHistory.assignment_group` through
    #: and :class:`devilry.apps.core.models.examiner.Examiner` or :class:`devilry.apps.core.models.candidate.Candidate`.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    #: When this entry was created.
    created_datetime = models.DateTimeField(
        null=False, blank=False, default=timezone.now
    )

    #: This defines the kind of operation this entry was created from, either a ``insert``, ``update`` or ``delete``
    #: database operation.
    #:
    #: If ``True``, the user was added to an ``AssignmentGroup``.
    #: If ``False``, the user was removed from the ``AssignmentGroup``.
    is_add = models.BooleanField(
        null=False, blank=False
    )

    class Meta:
        abstract = True


class ExaminerAssignmentGroupHistory(AbstractExaminerCandidateAssignmentGroupHistory):
    """
    An entry of this is model created if a :class:`devilry.apps.core.models.examiner.Examiner`-entry is inserted or
    deleted.
    """
    class Meta:
        verbose_name = 'Examiner assignment group history'
        verbose_name_plural = 'Examiner assignment group histories'


class CandidateAssignmentGroupHistory(AbstractExaminerCandidateAssignmentGroupHistory):
    """
    An entry of this is model created if a :class:`devilry.apps.core.models.candidate.Candidate`-entry is inserted or
    deleted.
    """
    class Meta:
        verbose_name = 'Candidate group history'
        verbose_name_plural = 'Candidate group histories'
