from django.db import models

from .abstract_is_admin import AbstractIsAdmin
from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_account.models import User


class Examiner(models.Model, AbstractIsAdmin):
    """
    .. attribute:: assignmentgroup

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: user

        A foreign key to a User.
    """

    class Meta:
        app_label = 'core'
        unique_together = ('relatedexaminer', 'assignmentgroup')
        db_table = 'core_assignmentgroup_examiners'

    #: Will be removed in 3.0 - see https://github.com/devilry/devilry-django/issues/812
    old_reference_not_in_use_user = models.ForeignKey(User, null=True, default=None, blank=True, on_delete=models.CASCADE)

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`
    #: where this examiner belongs.
    assignmentgroup = models.ForeignKey('AssignmentGroup', related_name='examiners', on_delete=models.CASCADE)

    #: ForeignKey to :class:`devilry.apps.core.models.relateduser.RelatedExaminer`
    #: (the model that ties User as examiner on a Period).
    relatedexaminer = models.ForeignKey(RelatedExaminer, on_delete=models.CASCADE)

    def get_anonymous_name(self):
        """
        Get the anonymous name of this examiner.
        """
        return self.relatedexaminer.get_anonymous_name()

    def __str__(self):
        return 'Examiner {} for {}'.format(
            self.relatedexaminer, self.assignmentgroup
        )
