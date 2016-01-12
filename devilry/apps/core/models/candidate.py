from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

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
    .. attribute:: assignment_group

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: student

        A student (a foreign key to a User).

    .. attribute:: candidate_id

        A optional candidate id. This can be anything as long as it is not
        more than 30 characters. When the assignment is anonymous, this is
        the "name" shown to examiners instead of the username of the
        student.
    """
    objects = CandidateQuerySet.as_manager()

    class Meta:
        app_label = 'core'

    #: Will be removed in 3.0 - see https://github.com/devilry/devilry-django/issues/810
    student = models.ForeignKey(User)

    #: ForeignKey to :class:`devilry.apps.core.models.relateduser.RelatedStudent`
    #: (the model that ties User as student on a Period).
    relatedstudent = models.ForeignKey(RelatedStudent,
                                       null=True, default=None, blank=True)

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`
    #: where this candidate belongs.
    assignment_group = models.ForeignKey(
        'AssignmentGroup',
        related_name='candidates')

    #: A candidate ID imported from a third party system.
    #: Only used if ``uses_custom_candidate_ids==True`` on the assignment.
    candidate_id = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='An optional candidate id. This can be anything as long as it '
                  'is less than 30 characters. Used to show the user on anonymous assignmens.')

    def __unicode__(self):
        return 'Candiate id={id}, student={student}, group={group}'.format(
            id=self.id,
            student=self.student,
            group=self.assignment_group)
