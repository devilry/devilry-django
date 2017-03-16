# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.utils import timezone

# Devilry/cradmin imports
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import models as group_models
from devilry.devilry_group.feedbackfeed_builder import builder_base


class FeedbackFeedTimelineBuilder(builder_base.FeedbackFeedBuilderBase):
    """
    Builds a sorted timeline of events that occur in the feedbackfeed.
    Generates a dictionary of events such as comments, new deadlines, expired deadlines and grading.
    """
    def __init__(self, **kwargs):
        """
        Initialize instance of :class:`~FeedbackFeedTimelineBuilder`.

        Args:
            group: An :obj:`~devilry.apps.core.AssignmentGroup` object.
            feedbacksets: Fetched feedbacksets, comments and files.
        """
        super(FeedbackFeedTimelineBuilder, self). __init__(**kwargs)
        self.timeline = {}

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
                    "deadline_datetime": feedbackset.deadline_datetime,
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
                        "deadline_datetime": current_deadline,
                        "feedbackset": feedbackset
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
                "feedbackset": feedbackset,
                'assignment': self.assignment
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
            event_dict['candidate'] = self._get_candidate_from_user(user=group_comment.user)
        elif group_comment.user_role == Comment.USER_ROLE_EXAMINER:
            event_dict['examiner'] = self._get_examiner_from_user(user=group_comment.user)
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

    def __add_deadline_moved_event(self, feedbackset):
        deadline_history_queryset = feedbackset.feedbacksetdeadlinehistory_set \
            .order_by('-changed_datetime')
        last_deadline_history = None
        if deadline_history_queryset.count() > 0:
            last_deadline_history = deadline_history_queryset[0]
        for deadline_history in deadline_history_queryset:
            is_last = False
            if deadline_history.changed_datetime == last_deadline_history.changed_datetime:
                is_last = True
            self.__add_event_item_to_timeline(
                datetime=deadline_history.changed_datetime,
                event_dict={
                    'type': 'deadline_moved',
                    'is_last': is_last,
                    'obj': deadline_history,
                    'feedbackset': feedbackset
                }
            )

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
        self.__add_deadline_moved_event(feedbackset=feedbackset)
        self.__add_deadline_created_to_timeline(feedbackset=feedbackset)
        self.__add_deadline_expired_if_needed(feedbackset=feedbackset)
        self.__add_grade_to_timeline_if_published(feedbackset=feedbackset)
        self.__add_comments_to_timeline(feedbackset=feedbackset)

    def build(self):
        """
        Build is called on an instance of :class:`~.FeedbackFeedTimelineBuilder` and builds the timeline
        and then sorts it.
        """
        for feedbackset in self.feedbacksets:
            self.__add_feedbackset_to_timeline(feedbackset=feedbackset)
        self.timeline = self.sort_dict(self.timeline)

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
