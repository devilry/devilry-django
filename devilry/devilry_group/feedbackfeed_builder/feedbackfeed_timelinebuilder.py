# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime

# Django imports
from django.utils import timezone

# Devilry/cradmin imports
from devilry.devilry_group.models import GroupComment
from devilry.devilry_group.feedbackfeed_builder import builder_base


class AbstractTimelineBuilder(object):
    def build(self):
        raise NotImplementedError()

    def _add_event_item_to_timeline(self, datetime_obj, event_dict):
        """
        General function for adding an event to the timeline.
        An event item is anything that occurs on the feedbackfeed that can
        be sorted; a comment, deadline created, deadline expired and grading.

        Args:
            datetime_obj: The datetime the event should be ordered by.
            event_dict: The event dictionary.
        """
        if datetime_obj is None:
            return
        if datetime_obj not in self.time_line:
            self.time_line[datetime_obj] = []
        event_dict['ordering_datetime'] = datetime_obj
        self.time_line[datetime_obj].append(event_dict)

    def get_as_list(self):
        """
        Get a flat list of event dictionaries.

        Returns:
             list: List of event-dictionaries.
        """
        timeline_list = []
        for datetime_obj in sorted(self.time_line.keys()):
            for event_dict in self.time_line[datetime_obj]:
                timeline_list.append(event_dict)
        return timeline_list

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


class FeedbackFeedTimelineBuilder(AbstractTimelineBuilder, builder_base.FeedbackFeedBuilderBase):
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
        self.time_line = {}

    def get_as_list_flat(self):
        timeline_list = []
        for datetime_obj in sorted(self.time_line.keys()):
            for event_dict in self.time_line[datetime_obj]:
                timeline_list.append(event_dict)
                for feedbackset_event_dict in event_dict['feedbackset_events']:
                    timeline_list.append(feedbackset_event_dict)
        return timeline_list

    def __should_skip_feedback_set(self, feedback_set):
        """
        Skip adding merge type feedbackset if they are not graded or
        do have any public comments.

        Args:
            feedback_set: The ``FeedbackSet`` to check.

        Returns:
            ``True`` or ``False``.
        """
        if feedback_set.is_merge_type:
            if not feedback_set.grading_published_datetime and\
               not feedback_set.groupcomment_set.filter(visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE).exists():
                return True
        return False

    def __get_order_feedback_set_by_deadline_datetime(self, feedback_set):
        """
        Get the ordering object for FeedbackSets.

        If the ``feedback_set.feedbackset_type`` is a merge type, we subtract 1 millisecond
        from the ``feedback_set.deadline_datetime``. We always want the merged feedbacksets to come before the current
        last feedbackset.

        Else return the ``feedback_set.deadline_datetime`` as is.

        Args:
            feedback_set: A ``FeedbackSet`` instance.

        Returns:
            DateTime: Datetime object to order by.
        """
        if feedback_set.is_merge_type:
            return feedback_set.deadline_datetime - timezone.timedelta(microseconds=1)
        return feedback_set.deadline_datetime

    def build(self):
        for feedback_set in self.feedbacksets:
            if self.__should_skip_feedback_set(feedback_set=feedback_set):
                continue
            feedback_set_event = FeedbackSetEventTimeLine(
                feedback_set=feedback_set,
                assignment=self.assignment)
            feedback_set_event.build()
            self._add_event_item_to_timeline(
                datetime_obj=self.__get_order_feedback_set_by_deadline_datetime(feedback_set=feedback_set),
                event_dict={
                    'feedbackset': feedback_set,
                    'feedbackset_events': feedback_set_event.get_as_list()
                }
            )
        self.time_line = self.sort_dict(self.time_line)


class FeedbackSetEventTimeLine(AbstractTimelineBuilder):
    """
    """
    def __init__(self, feedback_set, assignment):
        super(FeedbackSetEventTimeLine, self).__init__()
        self.feedback_set = feedback_set
        self.assignment = assignment
        self.time_line = {}

    def __add_deadline_expired_if_needed(self):
        """
        Adds a deadline_expired event type to the timeline.
        The expired deadline is the :func:`devilry.devilry_group.models.FeedbackSet.current_deadline` of
        ``feedbackset``.
        """
        current_deadline = self.feedback_set.current_deadline(assignment=self.assignment)
        if current_deadline is None:
            return
        if current_deadline <= timezone.now():
            self._add_event_item_to_timeline(
                    datetime_obj=current_deadline,
                    event_dict={
                        "type": "deadline_expired",
                        "deadline_datetime": current_deadline,
                        "feedbackset": self.feedback_set
                    })

    def __add_grade_to_timeline_if_published(self):
        """
        Add a grade event when the :obj:`devilry.devilry_group.models.FeedbackSet.grading_published_datetime` is set for
        ``feedbackset``.
        """
        grade_points = self.feedback_set.grading_points
        if len(self.feedback_set.grading_updates) > 0:
            grade_points = self.feedback_set.grading_updates[0].old_grading_points
        self._add_event_item_to_timeline(
            datetime_obj=self.feedback_set.grading_published_datetime,
            event_dict={
                'type': 'grade',
                'feedbackset': self.feedback_set,
                'grade_points': grade_points,
                'assignment': self.assignment
            }
        )

    def __add_comment_to_timeline(self, group_comment):
        """
        Adds a :class:`devilry.devilry_group.models.GroupComment` to the timeline.

        Args:
            group_comment: The comment to add.
        """
        event_dict = {
            "type": "comment",
            "obj": group_comment,
            "related_deadline": self.feedback_set.current_deadline(assignment=self.assignment),
        }
        self._add_event_item_to_timeline(
            datetime_obj=group_comment.published_datetime,
            event_dict=event_dict
        )

    def __add_comments_to_timeline(self):
        """
        Iterates through the comments for ``feedbackset`` and adds them to the time-line.
        """
        for group_comment in self.feedback_set.groupcomment_set.all():
            self.__add_comment_to_timeline(group_comment=group_comment)

    def __add_deadline_moved_event(self):
        """
        Iterates through the log entries for changes in the :obj:`~.devilry.devilry_group.models.FeedbackSet`s
        deadline_datetime and adds them to the time-line.
        """
        deadline_history_queryset = self.feedback_set.feedbacksetdeadlinehistory_set \
            .order_by('-changed_datetime')
        last_deadline_history = None
        if deadline_history_queryset.count() > 0:
            last_deadline_history = deadline_history_queryset[0]
        for deadline_history in deadline_history_queryset:
            is_last = False
            if deadline_history.changed_datetime == last_deadline_history.changed_datetime:
                is_last = True
            self._add_event_item_to_timeline(
                datetime_obj=deadline_history.changed_datetime,
                event_dict={
                    'type': 'deadline_moved',
                    'is_last': is_last,
                    'obj': deadline_history,
                    'feedbackset': self.feedback_set
                }
            )

    def __add_grading_updated_event(self):
        """
        Add event for updated grading on a :class:`~.devilry.devilry_group.models.FeedbackSet`.
        """
        grading_updates_length = len(self.feedback_set.grading_updates)
        for index, grading_updated in enumerate(self.feedback_set.grading_updates):
            if index+1 == grading_updates_length:
                next_grading_points = self.feedback_set.grading_points
            else:
                next_grading_points = self.feedback_set.grading_updates[index+1].old_grading_points
            self._add_event_item_to_timeline(
                datetime_obj=grading_updated.updated_datetime,
                event_dict={
                    'type': 'grading_updated',
                    'obj': grading_updated,
                    'next_grading_points': next_grading_points,
                    'feedbackset': self.feedback_set
                }
            )

    def build(self):
        self.__add_deadline_moved_event()
        self.__add_deadline_expired_if_needed()
        self.__add_grade_to_timeline_if_published()
        self.__add_comments_to_timeline()
        self.__add_grading_updated_event()
        self.time_line = self.sort_dict(self.time_line)
