# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
import collections
import datetime

# Django imports
from django.db import models
from django.utils import timezone

# Devilry/cradmin imports
from devilry.devilry_comment.models import CommentFile, Comment
from devilry.devilry_group import models as group_models


class FeedbackFeedTimelineBuilder(object):
    """
    Builds a sorted timeline of events that occur in the feedbackfeed.
    Generates a dictionary of events such as comments, new deadlines, expired deadlines and grading.
    """
    def __init__(self, group, requestuser, devilryrole):
        """
        Initialize instance of :class:`~FeedbackFeedTimelineBuilder`.

        Args:
            group: An :obj:`~devilry.apps.core.AssignmentGroup` object.
            requestuser: The requestuser.
            devilryrole: The role of the requestuser.
            feedbacksets: Fetched feedbacksets, comments and files.
        """
        self.requestuser = requestuser
        self.devilryrole = devilryrole
        self.group = group
        self.feedbacksets = list(self.__get_feedbackset_queryset())
        self.__candidatemap = self.__make_candidatemap()
        self.__examinermap = self.__make_examinermap()
        self.timeline = {}

    def __get_feedbackset_queryset(self):
        """
        NOTE: Should be moved to the base feedbackfeed view as it is reused.

        Get FeedbackSets' for the AssignmentGroup filtering on which comments
        should be shown in the feedbackfeed.

        Returns:
            QuerySet: FeedbackSet queryset.
        """
        commentfile_queryset = CommentFile.objects\
            .select_related('comment__user')\
            .order_by('filename')
        groupcomment_queryset = group_models.GroupComment.objects\
            .exclude_private_comments_from_other_users(user=self.requestuser)\
            .select_related(
                'user',
                'feedback_set__created_by',
                'feedback_set__grading_published_by')\
            .prefetch_related(models.Prefetch('commentfile_set', queryset=commentfile_queryset))
        if self.devilryrole == 'student':
            groupcomment_queryset = groupcomment_queryset\
                .filter(visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)\
                .exclude_is_part_of_grading_feedbackset_unpublished()
        return group_models.FeedbackSet.objects\
            .filter(group=self.group)\
            .prefetch_related(models.Prefetch('groupcomment_set', queryset=groupcomment_queryset))\
            .order_by('created_datetime')

    def __make_candidatemap(self):
        """
        Create a map of :class:`devilry.apps.core.models.Candidate` objects with user id as key.

        Returns:
            dict: Map of candidates.
        """
        candidatemap = {}
        for candidate in self.group.candidates.all():
            candidatemap[candidate.relatedstudent.user_id] = candidate
        return candidatemap

    def __make_examinermap(self):
        """
        Create a map of :class:`devilry.apps.core.models.Examiner` objects with user id as key.

        Returns:
             dict: Map of examiners.
        """
        examinermap = {}
        for examiner in self.group.examiners.all():
            examinermap[examiner.relatedexaminer.user_id] = examiner
        return examinermap

    def __get_candidate_from_user(self, user):
        """
        Get the :class:`devilry.apps.core.models.Candidate` object based on the user from the
        candidate map.

        Args:
            user: A class:`devilry.devilry_account.models.User` object.

        Returns:
             :class:`devilry.apps.core.models.Candidate`: A candidate or None.
        """
        return self.__candidatemap.get(user.id)

    def __get_examiner_from_user(self, user):
        """
        Get the :class:`devilry.apps.core.models.Candidate` object based on the user from the
        examiner map.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        Returns:
             :class:`devilry.apps.core.models.Examiner`: An examiner or None.
        """
        return self.__examinermap.get(user.id)

    def get_last_feedbackset(self):
        """
        Get the last :class:`devilry.devilry_group.models.FeedbackSet`.

        Returns:
             The last :class:`devilry.devilry_group.models.FeedbackSet`
        """
        if self.feedbacksets:
            return self.feedbacksets[-1]
        else:
            return None

    def __get_first_feedbackset(self):
        """
        Get the first :class:`devilry.devilry_group.models.FeedbackSet`.

        Returns:
             :class:`devilry.devilry_group.models.FeedbackSet`: The first FeedbackSet or None.
        """
        if self.feedbacksets:
            return self.feedbacksets[0]
        else:
            return None

    def get_last_deadline(self):
        """
        Get the :obj:`devilry.devilry_group.models.FeedbackSet.deadline_datetime` of the last
        FeedbackSet.

        Returns:
             DateTime: Deadline datetime or None.
        """
        last_feedbackset = self.get_last_feedbackset()
        if last_feedbackset:
            return self.__get_deadline_for_feedbackset(feedbackset=last_feedbackset)
        else:
            return None

    def __get_deadline_for_feedbackset(self, feedbackset):
        """
        Get the :obj:`devilry.devilry_group.models.FeedbackSet.deadline_datetime` for the ``feedbackset``.

        Args:
            feedbackset: Get deadline from.

        Returns:
            DateTime: Current deadline for ``feedbackset``(may be None).
        """
        return feedbackset.current_deadline(assignment=self.group.parentnode)

    def __add_event_item_to_timeline(self, datetime, event_dict):
        """
        General function for adding an event to the timeline.
        An event item is anything that occurs on the feedbackfeed that can
        be sorted; a comment, deadline created, deadline expired and grading.

        Args:
            datetime: The datetime the event should be ordered by.
            event_dict: The event dictionary.
        """
        if datetime is None:
            return
        if datetime not in self.timeline:
            self.timeline[datetime] = []
        event_dict['ordering_datetime'] = datetime
        self.timeline[datetime].append(event_dict)

    def __add_deadline_created_to_timeline(self, feedbackset):
        """
        Adds a deadline_created event type to the timeline.
        A deadline_created event is when a :class:`devilry.devilry_group.models.FeedbackSet` is created
        and the :obj:`devilry.devilry_group.models.FeedbackSet.feedbackset_type` is ``FEEDBACKSET_TYPE_NEW_ATTEMPT``.

        Args:
            feedbackset: FeedbackSet to add to the timeline.
        """
        if feedbackset.feedbackset_type == group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
            return
        self.__add_event_item_to_timeline(
                datetime=feedbackset.created_datetime,
                event_dict={
                    "type": "deadline_created",
                    "feedbackset": feedbackset
                })

    def __add_deadline_expired_if_needed(self, feedbackset):
        """
        Adds a deadline_expired event type to the timeline.
        The expired deadline is the :func:`devilry.devilry_group.models.FeedbackSet.current_deadline` of
        ``feedbackset``.

        Args:
            feedbackset: Get deadline from.
        """
        current_deadline = self.__get_deadline_for_feedbackset(feedbackset=feedbackset)
        if current_deadline is None:
            return
        if current_deadline <= timezone.now():
            self.__add_event_item_to_timeline(
                    datetime=current_deadline,
                    event_dict={
                        "type": "deadline_expired",
                        "deadline_datetime": current_deadline
                    })

    def __add_grade_to_timeline_if_published(self, feedbackset):
        """
        Add a grade event when the :obj:`devilry.devilry_group.models.FeedbackSet.grading_published_datetime` is set for
        ``feedbackset``.

        Args:
            feedbackset: Get published grading datetime from.
        """
        self.__add_event_item_to_timeline(
            datetime=feedbackset.grading_published_datetime,
            event_dict={
                "type": "grade",
                "feedbackset": feedbackset
            }
        )

    def __add_comment_to_timeline(self, group_comment, feedbackset):
        """
        Adds a :class:`devilry.devilry_group.models.GroupComment` to the timeline.

        Args:
            group_comment: The comment to add.
            feedbackset: The feedbackset the comment belongs to.
        """
        event_dict = {
            "type": "comment",
            "obj": group_comment,
            "related_deadline": self.__get_deadline_for_feedbackset(feedbackset=feedbackset),
        }
        if group_comment.user_role == Comment.USER_ROLE_STUDENT:
            event_dict['candidate'] = self.__get_candidate_from_user(user=group_comment.user)
        elif group_comment.user_role == Comment.USER_ROLE_EXAMINER:
            event_dict['examiner'] = self.__get_examiner_from_user(user=group_comment.user)
        self.__add_event_item_to_timeline(
            datetime=group_comment.published_datetime,
            event_dict=event_dict
        )

    def __add_comments_to_timeline(self, feedbackset):
        """
        Iterates through the comments for ``feedbackset`` and adds them to the timeline.

        Args:
             feedbackset: Feedbackset to get comments from.
        """
        for group_comment in feedbackset.groupcomment_set.all():
            self.__add_comment_to_timeline(group_comment=group_comment, feedbackset=feedbackset)

    def __add_feedbackset_to_timeline(self, feedbackset):
        """
        Adds events to the timeline by calling the functions for adding specific events.

        See documentation for functions:
            ``__add_deadline_created_to_timeline()``
            ``__add_deadline_expired_if_needed()``
            ``__add_grade_to_timeline_if_published()``
            ``__add_comments_to_timeline()``

        Args:
            feedbackset: Current feedbackset to add events for.
        """
        self.__add_deadline_created_to_timeline(feedbackset=feedbackset)
        self.__add_deadline_expired_if_needed(feedbackset=feedbackset)
        self.__add_grade_to_timeline_if_published(feedbackset=feedbackset)
        self.__add_comments_to_timeline(feedbackset=feedbackset)

    def __sort_timeline(self):
        """
        Sorts the timeline after all events are added.
        """
        def compare_timeline_items(timeline_item_a, timeline_item_b):
            datetime_a = timeline_item_a[0]
            datetime_b = timeline_item_b[0]
            if datetime_a is None:
                datetime_a = datetime.datetime(1970, 1, 1)
            if datetime_b is None:
                datetime_b = datetime.datetime(1970, 1, 1)
            return cmp(datetime_a, datetime_b)
        self.timeline = collections.OrderedDict(sorted(self.timeline.items(), compare_timeline_items))

    def build(self):
        """
        Build is called on an instance of :class:`~.FeedbackFeedTimelineBuilder` and builds the timeline
        and then sorts it.
        """
        for feedbackset in self.feedbacksets:
            self.__add_feedbackset_to_timeline(feedbackset=feedbackset)
        self.__sort_timeline()

    def get_as_list(self):
        """
        Get a flat list of event dictionaries.

        Returns:
             list: List of event-dictionaries.
        """
        timeline_list = []
        for datetime in sorted(self.timeline.keys()):
            for event_dict in self.timeline[datetime]:
                timeline_list.append(event_dict)
        return timeline_list
