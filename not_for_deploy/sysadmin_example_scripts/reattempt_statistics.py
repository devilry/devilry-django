#!/usr/bin/env python
import os

import django


def get_all_subjects():
    """
    Get all subjects with more than one period and annonate with active_period_objects
    """
    from devilry.apps.core.models import Subject

    subject_queryset = Subject.objects.all().prefetch_active_period_objects()

    return subject_queryset


def get_all_assignments_in_period(period):
    """
    Fetch all assignments for a given period
    """
    return period.assignments.all()


def get_assignments_with_matching_shortname_in_previous_periods(subject, assignment):
    """
    Fetch the assignments in earlier periods with same subject that have equal matching shortname

    E.g. oblig1 - 2019 matches oblig1 - 2020
    """
    from devilry.apps.core.models import Assignment
    short_name = assignment.short_name
    assignments = Assignment.objects.none()
    for period in subject.periods.exclude(id=assignment.period.id):
        assignments = assignments.union(period.assignments.filter(short_name=short_name))
    return assignments


def print_assignment_statistics(assignment):
    """
    Fetch the statistics from the given assignments

    - Assignment name
    - The total number of assignment groups within the given assignment
    - The total number of first attempts given within all feedbackset across all groups within assignment
    - The total number of first attempts with no deliveries within all feedbackset across all groups within assignment
    - The total number of first attempts with deliveries within all feedbackset across all groups within assignment
    - The total number of new attempts given within all feedbackset across all groups within assignment
    - The total number of new attempts with no deliveries within all feedbackset across all groups within assignment
    - The total number of new attempts with deliveries within all feedbackset across all groups within assignment
    - The total number of moved deadlines with no deliveries in feedbackset across all groups within assignment
    """
    from devilry.devilry_group.models import (FeedbackSet,
                                              FeedbackSetDeadlineHistory,
                                              GroupComment)
    from django.db.models import F
    statistics = {
        'assignment': assignment,
        'number_of_groups': assignment.assignmentgroups.all().count(),
        'number_of_firstattempts': 0,
        'number_of_newattempts': 0,
        'number_of_firstattempts_with_no_delivery': 0,
        'number_of_newattempts_with_no_delivery': 0,
        'number_of_firstattempts_with_deliveries': 0,
        'number_of_newattempts_with_deliveries': 0,
        'number_of_moved_deadlines_with_no_delivery': 0
    }
    for group in assignment.assignmentgroups.all():
        feedbackset_queryset = FeedbackSet.objects\
            .filter(group=group)
        for feedbackset in feedbackset_queryset:
            number_of_group_comment_from_student = GroupComment.objects\
                .filter(user_role=GroupComment.USER_ROLE_STUDENT)\
                .filter(feedback_set=feedbackset).count()
            if feedbackset.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT:
                statistics['number_of_newattempts'] += 1
                if number_of_group_comment_from_student == 0:
                    statistics['number_of_newattempts_with_no_delivery'] += 1
                else:
                    statistics['number_of_newattempts_with_deliveries'] += 1
            elif feedbackset.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
                statistics['number_of_firstattempts'] += 1
                if number_of_group_comment_from_student == 0:
                    statistics['number_of_firstattempts_with_no_delivery'] += 1
                else:
                    statistics['number_of_firstattempts_with_deliveries'] += 1
            feedbackset_deadline_edit_count = FeedbackSetDeadlineHistory.objects.filter(
                            feedback_set=feedbackset).filter(deadline_old__lt=F('deadline_new')).count()
            statistics['number_of_moved_deadlines_with_no_delivery'] += feedbackset_deadline_edit_count

    print("{assignment},{number_of_groups},{number_of_firstattempts},{number_of_newattempts},{number_of_firstattempts_with_no_delivery},{number_of_newattempts_with_no_delivery},{number_of_firstattempts_with_deliveries},{number_of_newattempts_with_deliveries},{number_of_moved_deadlines_with_no_delivery}".format(
                        **statistics))
    return statistics


if __name__ == "__main__":
    # For development:
    os.environ.setdefault('DJANGOENV', 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    # For production: Specify python path to your settings file here
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry_settings')
    # django.setup()

    # Get number of deliveries
    subject_set = get_all_subjects()
    print("'assignment', 'number_of_groups', 'number_of_firstattempts', 'number_of_newattempts', 'number_of_firstattempts_with_no_delivery', 'number_of_newattempts_with_no_delivery', 'number_of_firstattempts_with_deliveries', 'number_of_newattempts_with_deliveries', 'number_of_moved_deadlines_with_no_delivery'")
    for subject in subject_set:
        for period in subject.active_period_objects:
            for assignment in get_all_assignments_in_period(period):
                print_assignment_statistics(assignment)
                assignments_with_similar_shortname = get_assignments_with_matching_shortname_in_previous_periods(
                    subject, assignment)
                for assignment_with_similar_shortname in assignments_with_similar_shortname:
                    print_assignment_statistics(assignment_with_similar_shortname)
