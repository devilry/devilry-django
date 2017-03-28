# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime

from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Examiner
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
    groupcomment_queryset = group_models.GroupComment.objects\
        .exclude_private_comments_from_other_users(user=requestuser)\
        .select_related(
            'user',
            'feedback_set',
            'feedback_set__created_by',
            'feedback_set__grading_published_by')\
        .prefetch_related(models.Prefetch('commentfile_set', queryset=commentfile_queryset))
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
        .order_by('created_datetime')


class FeedbackFeedBuilderBase(object):
    """
    """
    def __init__(self, assignment, group, feedbacksets):
        super(FeedbackFeedBuilderBase, self).__init__()
        self.assignment = assignment
        self.group = self._prefetch_candidates_and_examiners_for_group(group)
        self.feedbacksets = list(feedbacksets)
        self._candidate_map = self._make_candidate_map()
        self._examiner_map = self._make_examiner_map()

    def _prefetch_candidates_and_examiners_for_group(self, group):
        return AssignmentGroup.objects\
            .prefetch_related(
                models.Prefetch('candidates', queryset=self._get_candidatequeryset()))\
            .prefetch_related(
                models.Prefetch('examiners', queryset=self._get_examinerqueryset()))\
            .get(id=group.id)

    def _get_candidatequeryset(self):
        """Get candidates.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Candidate`s.
        """
        return Candidate.objects \
            .select_related('relatedstudent', 'relatedstudent__period', 'relatedstudent__user')

    def _get_examinerqueryset(self):
        """Get examiners.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Examiner`s.
        """
        return Examiner.objects \
            .select_related('relatedexaminer', 'relatedexaminer__period', 'relatedexaminer__user')

    def _make_candidate_map(self):
        """
        Create a map of :class:`devilry.apps.core.models.Candidate` objects with user id as key.

        Returns:
            dict: Map of candidates.
        """
        candidatemap = {}
        for candidate in self.group.candidates.all():
            candidatemap[candidate.relatedstudent.user_id] = candidate
        return candidatemap

    def _make_examiner_map(self):
        """
        Create a map of :class:`devilry.apps.core.models.Examiner` objects with user id as key.

        Returns:
             dict: Map of examiners.
        """
        examinermap = {}
        for examiner in self.group.examiners.all():
            examinermap[examiner.relatedexaminer.user_id] = examiner
        return examinermap

    def _get_candidate_from_user(self, user):
        """
        Get the :class:`devilry.apps.core.models.Candidate` object based on the user from the
        candidate map.

        Args:
            user: A class:`devilry.devilry_account.models.User` object.

        Returns:
             :class:`devilry.apps.core.models.Candidate`: A candidate or None.
        """
        return self._candidate_map.get(user.id)

    def _get_examiner_from_user(self, user):
        """
        Get the :class:`devilry.apps.core.models.Candidate` object based on the user from the
        examiner map.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        Returns:
             :class:`devilry.apps.core.models.Examiner`: An examiner or None.
        """
        return self._examiner_map.get(user.id)

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