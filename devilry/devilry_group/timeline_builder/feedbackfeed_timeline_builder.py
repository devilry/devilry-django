import collections
import datetime

from django.db import models
from django.utils import timezone

from devilry.devilry_comment.models import CommentFile, Comment
from devilry.devilry_group import models as group_models


class FeedbackFeedTimelineBuilder(object):
    """

    """
    def __init__(self, group, requestuser, devilryrole):
        self.requestuser = requestuser
        self.devilryrole = devilryrole
        self.group = group
        self.feedbacksets = list(self.__get_feedbackset_queryset())
        self.__candidatemap = self.__make_candidatemap()
        self.__examinermap = self.__make_examinermap()
        self.timeline = {}

    def __get_feedbackset_queryset(self):
        """
        Retrieves the comments a user has access to.
        This function must be implemented by subclasses of :class:`~.FeedbackFeedBaseView`

        :param group:
            The :class:`devilry.apps.core.models.AssignmentGroup` the user belongs to.

        Returns:
            List of :class:`devilry.devilry_group.models.GroupComment` objects.

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
        candidatemap = {}
        for candidate in self.group.candidates.all():
            candidatemap[candidate.relatedstudent.user_id] = candidate
        return candidatemap

    def __make_examinermap(self):
        examinermap = {}
        for examiner in self.group.examiners.all():
            examinermap[examiner.relatedexaminer.user_id] = examiner
        return examinermap

    def __get_candidate_from_user(self, user):
        return self.__candidatemap.get(user.id, None)

    def __get_examiner_from_user(self, user):
        return self.__examinermap.get(user.id, None)

    def get_last_feedbackset(self):
        if self.feedbacksets:
            return self.feedbacksets[-1]
        else:
            return None

    def __get_first_feedbackset(self):
        if self.feedbacksets:
            return self.feedbacksets[0]
        else:
            return None

    def get_last_deadline(self):
        last_feedbackset = self.get_last_feedbackset()
        if last_feedbackset:
            return self.__get_deadline_for_feedbackset(feedbackset=last_feedbackset)
        else:
            return None

    def __get_deadline_for_feedbackset(self, feedbackset):
        """

        Args:
            index:
            feedbackset:

        Returns:

        """
        return feedbackset.current_deadline(assignment=self.group.parentnode)

    def __add_event_item_to_timeline(self, datetime, event_dict):
        """
        General function for adding an event to the timeline.
        An event item is everything that occurs on the feedbackfeed that can
        be sorted; a comment, deadline created, deadline expired and grading.

        Args:
            datetime: The time the event is sorted on
            event_dict: The event object.
        """
        if datetime is None:
            return
        if datetime not in self.timeline:
            self.timeline[datetime] = []
        event_dict['ordering_datetime'] = datetime
        self.timeline[datetime].append(event_dict)

    def __add_deadline_created_to_timeline(self, feedbackset):
        """

        Args:
            feedbackset:

        Returns:

        """
        if feedbackset.feedbackset_type == group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
            return
        current_deadline = self.__get_deadline_for_feedbackset(feedbackset=feedbackset)
        self.__add_event_item_to_timeline(
                datetime=feedbackset.created_datetime,
                event_dict={
                    "type": "deadline_created",
                    "feedbackset": feedbackset
                })

    def __add_deadline_expired_if_needed(self, feedbackset):
        """

        Args:
            feedbackset:

        Returns:

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

        Args:
            deadline_datetime:
            feedbackset:

        Returns:

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

        Args:
            group_comment:
            feedbackset:

        Returns:

        """
        event_dict = {
            "type": "comment",
            "obj": group_comment,
            "related_deadline": self.__get_deadline_for_feedbackset(feedbackset=feedbackset),
        }
        if group_comment.user_role == Comment.USER_ROLE_STUDENT:
            cand = self.__get_candidate_from_user(user=group_comment.user)
            event_dict['candidate'] = cand
        elif group_comment.user_role == Comment.USER_ROLE_EXAMINER:
            examiner = self.__get_examiner_from_user(user=group_comment.user)
            event_dict['examiner'] = examiner
        self.__add_event_item_to_timeline(
            datetime=group_comment.published_datetime,
            event_dict=event_dict
        )

    def __add_comments_to_timeline(self, feedbackset):
        """

        Args:
            feedbackset:

        Returns:

        """
        for group_comment in feedbackset.groupcomment_set.all():
            self.__add_comment_to_timeline(group_comment=group_comment, feedbackset=feedbackset)

    def __add_feedbackset_to_timeline(self, feedbackset):
        """

        Args:
            feedbackset:

        Returns:

        """
        self.__add_deadline_created_to_timeline(feedbackset=feedbackset)
        self.__add_deadline_expired_if_needed(feedbackset=feedbackset)
        self.__add_grade_to_timeline_if_published(feedbackset=feedbackset)
        self.__add_comments_to_timeline(feedbackset=feedbackset)

    def __sort_timeline(self):
        """
        """
        def compare_timeline_items(a, b):
            datetime_a = a[0]
            datetime_b = b[0]
            if datetime_a is None:
                datetime_a = datetime.datetime(1970, 1, 1)
            if datetime_b is None:
                datetime_b = datetime.datetime(1970, 1, 1)
            return cmp(datetime_a, datetime_b)
        self.timeline = collections.OrderedDict(sorted(self.timeline.items(), compare_timeline_items))

    def build(self):
        """

        """
        for feedbackset in self.feedbacksets:
            self.__add_feedbackset_to_timeline(feedbackset=feedbackset)
        self.__sort_timeline()

    def get_as_list(self):
        """

        Returns:

        """
        timeline_list = []
        for datetime in sorted(self.timeline.keys()):
            for event_dict in self.timeline[datetime]:
                timeline_list.append(event_dict)
        return timeline_list
