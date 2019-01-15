#!/usr/bin/env python
import os
import argparse
import django
from datetime import datetime
import arrow

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models


def get_number_of_deliveries(from_datetime, to_datetime):
    """
    Get the number of deliveries made.

    Simply counts the number of comments posted by students with files on
    all FeedbackSets with deadlines within the from and to datetime arguments.
    """
    from devilry.devilry_comment.models import CommentFile
    from devilry.devilry_group.models import GroupComment, FeedbackSet

    #: Get all `FeedbackSets` with deadlines within the from and to datetime range.
    feedbackset_queryset = FeedbackSet.objects\
        .filter(deadline_datetime__gte=from_datetime,
                deadline_datetime__lte=to_datetime)

    #: UNCOMMENT THIS IF YOU WANT TO:
    #:
    #: Filter only the last FeedbackSet for the AssignmentGroup.
    # feedbackset_queryset = feedbackset_queryset \
    #     .filter(group__cached_data__last_feedbackset_id=models.F('id'))

    # Get all comments for all `FeedbackSet`s with deadline within the
    # from and to datetime posted by a student.
    group_comment_queryset = GroupComment.objects\
        .filter(user_role=GroupComment.USER_ROLE_STUDENT)\
        .filter(id__in=feedbackset_queryset.values_list('id', flat=True))

    #: UNCOMMENT THIS IF YOU WANT TO:
    #:
    #: Filter only comments posted before the deadline expired on the
    #: feedbackset the comment belongs to.
    # group_comment_queryset = group_comment_queryset\
    #     .filter(published_datetime__gte=models.F('feedback_set__deadline_datetime'))

    #: Get all Comments with files from the fetched comments.
    comment_file_queryset = CommentFile.objects\
        .filter(comment_id__in=group_comment_queryset.values_list('id', flat=True))

    return comment_file_queryset.count()


def get_unique_logins(from_datetime):
    """
    Get the number of unique logins since a specified datetime.
    """
    unique_logins = get_user_model().objects\
        .filter(last_login__gte=from_datetime)
    return unique_logins.count()


def populate_arguments_and_get_parser():
    parser = argparse.ArgumentParser(description='Set up department permission groups for missing subjects.')
    parser.add_argument(
        '--from-date',
        dest='from_date',
        default='1900-01-01',
        help='A %%Y-%%m-%%d formatted from-date. Defaults to 1900-01-01.')
    parser.add_argument(
        '--to-date',
        dest='to_date',
        default='5999-12-31',
        help='A %%Y-%%m-%%d formatted to-date. Defaults to 5999-12-31.')
    return parser


if __name__ == "__main__":
    # For development:
    os.environ.setdefault('DJANGOENV', 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    # For production: Specify python path to your settings file here
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry_settings')
    # django.setup()

    parser = populate_arguments_and_get_parser()
    args = parser.parse_args()
    arguments_dict = vars(args)

    from_datetime = timezone.make_aware(datetime.strptime(arguments_dict['from_date'], '%Y-%m-%d'))
    to_datetime = timezone.make_aware(datetime.strptime(arguments_dict['to_date'], '%Y-%m-%d'))

    # Get unique logins
    unique_login_count = get_unique_logins(from_datetime=from_datetime)
    print 'Unique logins since {}: {}'.format(
        arrow.get(from_datetime).format('MMM D. YYYY HH:mm'),
        unique_login_count)

    # Get number of deliveries
    delivery_count = get_number_of_deliveries(from_datetime, to_datetime)
    print 'Deliveries made between {} and {}: {}'.format(
        arrow.get(from_datetime).format('MMM D. YYYY HH:mm'),
        arrow.get(to_datetime).format('MMM D. YYYY HH:mm'),
        delivery_count
    )
