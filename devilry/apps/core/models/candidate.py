from django.conf import settings
from django.db import models

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import User


class CandidateQuerySet(models.QuerySet):
    def filter_has_passing_grade(self, assignment):
        """
        Filter only :class:`.Candidate` objects within the given
        assignment that has a passing grade.

        That means that this filters out all Candidates on AssignmentGroups
        the latest published :class:`devilry.devilry_group.models.FeedbackSet`
        has less :obj:`devilry.devilry_group.models.FeedbackSet.grading_points`
        than the ``passing_grade_min_points`` for the assignment.

        This method performs ``filter(assignment_group__parentnode=assignment)``
        in addition to the query that checks the feedbacksets.

        Args:
            assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
        """
        return self.filter(assignment_group__parentnode=assignment)\
            .extra(
                where=[
                    """
                    (
                        SELECT devilry_group_feedbackset.grading_points
                        FROM devilry_group_feedbackset
                        WHERE
                            devilry_group_feedbackset.group_id = core_candidate.assignment_group_id
                            AND
                            devilry_group_feedbackset.grading_published_datetime IS NOT NULL
                        ORDER BY devilry_group_feedbackset.grading_published_datetime DESC
                        LIMIT 1
                    ) >= %s
                    """
                ],
                params=[
                    assignment.passing_grade_min_points
                ]
            )


class Candidate(models.Model):
    """
    A student within an AssignmentGroup.

    A candidate is a many-to-many between :class:`devilry.apps.core.models.AssignmentGroup`
    and a user.
    """
    objects = CandidateQuerySet.as_manager()

    class Meta:
        app_label = 'core'

    #: Will be removed in 3.0 - see https://github.com/devilry/devilry-django/issues/810
    old_reference_not_in_use_student = models.ForeignKey(User, null=True, default=None, blank=True, on_delete=models.CASCADE)

    #: ForeignKey to :class:`devilry.apps.core.models.relateduser.RelatedStudent`
    #: (the model that ties User as student on a Period).
    relatedstudent = models.ForeignKey(RelatedStudent, on_delete=models.CASCADE)

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`
    #: where this candidate belongs.
    assignment_group = models.ForeignKey(
        'AssignmentGroup',
        related_name='candidates', on_delete=models.CASCADE)

    #: A candidate ID imported from a third party system.
    #: Only used if ``uses_custom_candidate_ids==True`` on the assignment.
    candidate_id = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='An optional candidate id. This can be anything as long as it '
                  'is less than 30 characters. Used to show the user on anonymous assignmens.')

    def get_anonymous_name(self, assignment=None):
        """
        Get the anonymous name of this candidate.

        Args:
            assignment: An optional :class:`devilry.apps.core.models.assignment.Assignment`.
                if this is provided, we use this instead of looking up
                ``assignment_group.parentnode``. This is essential for views
                that list many candidates since it avoid extra database lookups.
        """
        if assignment is None:
            assignment = self.assignment_group.parentnode
        if assignment.uses_custom_candidate_ids:
            if self.candidate_id:
                return self.candidate_id
            else:
                return self.relatedstudent.get_automatic_anonymous_id_with_fallback()
        else:
            return self.relatedstudent.get_anonymous_name()

    def __str__(self):
        return 'Candiate id={id}, student={student}, group={group}'.format(
            id=self.id,
            student=self.relatedstudent,
            group=self.assignment_group)
