#!/usr/bin/env python
import os

import django
import argparse
import arrow

from django.db import models
from django.utils import timezone


def get_arguments():
    parser = argparse.ArgumentParser(description='Fetch delivery statistics for Devilry users.')
    parser.add_argument(
        '--username-list',
        required=True,
        nargs='+',
        dest='username_list',
        help='A list of Devilry user shortnames. Example: --username-list username1 username2 username3'
    )
    parser.add_argument(
        '--subject-shortname',
        required=True,
        type=str,
        dest='subject_shortname',
        help='The shortname of a subject. This is unique.'
    )
    parser.add_argument(
        '--period-shortname',
        required=True,
        type=str,
        dest='period_shortname',
        help='The shortname of a period/semester. This is unique together with the subject shortname.'
    )
    return vars(parser.parse_args())


if __name__ == "__main__":
    # For development:
    os.environ.setdefault('DJANGOENV', 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    # For production: Specify python path to your settings file here
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry_settings')
    # django.setup()

    # Imports
    #
    # Must be done after django.setup()
    from django.conf import settings
    from devilry.apps.core.models import Period, Candidate
    from devilry.devilry_dbcache.models import AssignmentGroupCachedData
    from devilry.devilry_group.models import FeedbackSet, GroupComment
    from devilry.devilry_comment.models import CommentFile

    #
    # Get script arguments
    #
    argument_dict = get_arguments()

    #
    # Get Period
    #
    period = Period.objects \
        .get(
            parentnode__short_name=argument_dict['subject_shortname'],
            short_name=argument_dict['period_shortname']
        )

    #
    # Loop through each username, and collect data about each 
    # assignment on the period.
    #
    # 
    #
    now = timezone.now()
    serial_number = 10000
    for user_shortname in argument_dict['username_list']:

        #
        # Get all AssignmentGroups for the user on the Period.
        # The reason for not getting the Assignments directly, is 
        # because we still need the AssignmentGroup to collect further 
        # data about deadlines, comments, feedback etc.
        #
        assignment_group_cached_data = AssignmentGroupCachedData.objects \
            .select_related(
                'group',
                'group__parentnode',
                'group__parentnode__parentnode'
            ) \
            .filter(
                group__parentnode__publishing_time__lt=now,
                group_id__in=Candidate.objects \
                    .select_related(
                        'assignment_group',
                        'relatedstudent',
                        'relatedstudent__period'
                    ) \
                    .filter(
                        relatedstudent__user__shortname=user_shortname,
                        relatedstudent__period=period,
                        assignment_group__parentnode__parentnode=period
                    ) \
                    .values_list('assignment_group_id', flat=True)
            ) \
            .order_by('group__parentnode__first_deadline')

        #
        # Collect data from each AssignmentGroup (by extension the Assignment) 
        # for the user.
        #
        for cached_group_data in assignment_group_cached_data:
            # Get the last published FeedbackSet
            #
            # We only care about published/graded assignments.
            last_published_feedbackset = cached_group_data.last_published_feedbackset
            if not last_published_feedbackset:
                continue

            # Get timestampt for last delivery.
            #
            # The last delivery is the last comment from a student with files.
            last_student_comment_with_files = GroupComment.objects \
                .filter(
                    visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                    user_role=GroupComment.USER_ROLE_STUDENT,
                    comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                    feedback_set=last_published_feedbackset) \
                .annotate(
                    has_files=models.Exists(
                        CommentFile.objects.filter(comment_id=models.OuterRef('id'))
                    )
                ) \
                .filter(has_files=True) \
                .order_by('-published_datetime') \
                .last()
            last_delivery_datetime = None
            if last_student_comment_with_files:
                last_delivery_datetime = last_student_comment_with_files.published_datetime

            # Get number of feedbacks.
            #
            # Merged feedbacksets (groups with more than student) is ignored.
            feedback_num = FeedbackSet.objects \
                .filter(
                    group=cached_group_data.group,
                    ignored=False,
                    grading_published_datetime__isnull=False,
                    feedbackset_type__in=[
                        FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                        FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
                    ]
                ).count()

            print(
                f'{serial_number} - '
                f'{user_shortname} - '
                f'{cached_group_data.group.parentnode.parentnode.parentnode.short_name} - '
                f'{cached_group_data.group.parentnode.short_name} - '
                f'{arrow.get(cached_group_data.group.parentnode.first_deadline).to(settings.TIME_ZONE)} - '
                f'{arrow.get(last_delivery_datetime).to(settings.TIME_ZONE)} - '
                f'{cached_group_data.new_attempt_count + 1} - '
                f'{feedback_num}'
            )
            serial_number += 1
