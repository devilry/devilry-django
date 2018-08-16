# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime

from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_comment import models as comment_models
from devilry.devilry_group import models as group_models


def get_feedbackfeed_builder_queryset(group, requestuser, devilryrole):
    """
    Get a queryset containing prefetched :class:`~devilry.devilry_group.models.FeedbackSets`,
    :class:`~devilry.devilry_group.models.GroupComments` and :class:`~devilry.devilry_comment.models.CommentFiles`
    the requestuser har access to.

    Args:
        group (AssignmentGroup): The cradmin role.
        requestuser (User): The requestuser.
        devilryrole (str): Role for the requestuser.

    Returns:
        QuerySet: FeedbackSet queryset.
    """
    commentfile_queryset = comment_models.CommentFile.objects\
        .select_related('comment__user')\
        .order_by('filename')
    groupcomment_queryset = group_models.GroupComment.objects \
        .exclude_private_comments_from_other_users(user=requestuser) \
        .annotate_with_last_edit_history(requestuser_devilryrole=devilryrole)\
        .select_related(
            'user',
            'feedback_set',
            'feedback_set__created_by',
            'feedback_set__grading_published_by') \
        .prefetch_related(
            models.Prefetch(
                'commentfile_set',
                queryset=commentfile_queryset))
    feedbackset_deadline_history_queryset = group_models.FeedbackSetDeadlineHistory.objects.all()
    if devilryrole == 'student':
        groupcomment_queryset = groupcomment_queryset\
            .filter(visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)\
            .exclude_is_part_of_grading_feedbackset_unpublished()

    return group_models.FeedbackSet.objects\
        .select_related(
            'group',
            'group__parentnode',
            'group__parentnode__parentnode',
            'group__parentnode__parentnode__parentnode')\
        .filter(group=group)\
        .prefetch_related(
            models.Prefetch(
                'groupcomment_set',
                queryset=groupcomment_queryset))\
        .prefetch_related(
            models.Prefetch(
                'feedbacksetdeadlinehistory_set',
                queryset=feedbackset_deadline_history_queryset)
        )\
        .prefetch_related(
            models.Prefetch(
                'grading_update_histories',
                queryset=group_models.FeedbackSetGradingUpdateHistory.objects.all(),
                to_attr='grading_updates'
            )
        )\
        .order_by('created_datetime')


class FeedbackFeedBuilderBase(object):
    """
    """
    def __init__(self, assignment, group, feedbacksets):
        super(FeedbackFeedBuilderBase, self).__init__()
        self.assignment = assignment
        self.feedbacksets = list(feedbacksets)

    def sort_dict(self, dictionary):
        """
        Sorts the timeline after all events are added.

        Args:
            dictionary (dict): Dictionary of item with datetime keys.
        """
        def compare_items(item_a, item_b):
            datetime_a = item_a[0]
            datetime_b = item_b[0]
            if datetime_a is None:
                datetime_a = datetime.datetime(1970, 1, 1)
            if datetime_b is None:
                datetime_b = datetime.datetime(1970, 1, 1)
            return cmp(datetime_a, datetime_b)
        return collections.OrderedDict(sorted(dictionary.items(), compare_items))