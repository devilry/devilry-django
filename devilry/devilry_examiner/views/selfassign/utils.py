from django.db import models
from devilry.apps.core.models import RelatedExaminer, Assignment, AssignmentGroup, Period


def get_assignments_available_for_selfassign():
    # TODO: Search filters do not work with groups across anonymized 
    # and unanonymized assignments, so allowing anonymized assignments 
    # makes it possible to find anonymized users by searching for the 
    # actual name.
    # Excluding anonymized assignments for now.
    return Assignment.objects \
        .select_related('parentnode') \
        .filter_is_active() \
        .filter(
            anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF,
            examiners_can_self_assign=True
        )


def assignment_groups_available_for_self_assign(period, user):
    # Assignments the user has access to as a RelatedExaminer, 
    # where selfassign is enabled.
    assignment_queryset = get_assignments_available_for_selfassign() \
        .filter(
            parentnode_id__in=RelatedExaminer.objects \
                .select_related('period') \
                .filter(
                    user=user,
                    period=period,
                    active=True
                ).values_list('period_id', flat=True)
        )

    # AssignmentGroups
    assignmentgroup_queryset = AssignmentGroup.objects \
        .select_related('parentnode') \
        .filter(parentnode_id__in=assignment_queryset.values_list('id', flat=True)) \
        .annotate(number_of_examiners=models.Count('examiners')) \
        .filter(
            models.Q(examiners__relatedexaminer__user=user)
            |
            models.Q(number_of_examiners__lt=models.F('parentnode__examiner_self_assign_limit'))
        ).distinct()
    return assignmentgroup_queryset


def selfassign_available_periods(user):
    return Period.objects \
        .filter_active() \
        .filter(
            id__in=RelatedExaminer.objects \
                .select_related('period') \
                .filter(active=True, user=user) \
                .values_list('period_id', flat=True)
        ) \
        .annotate(
            has_assignments_with_selfassign_enabled=models.Exists(
                get_assignments_available_for_selfassign().filter(parentnode_id=models.OuterRef('id'))
            )
        ) \
        .filter(
            has_assignments_with_selfassign_enabled=True
        ) \
        .distinct()
