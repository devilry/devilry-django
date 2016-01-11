import collections
import datetime

from django.utils import timezone

from devilry.devilry_group import models as group_models


class FeedbackFeedTimelineBuilder(object):

    def __init__(self, view):
        self.viewclass = view

    def get_feedbacksets_for_group(self, group):
        """
        TODO: document

        :param group:
        :return:
        """
        return group_models.FeedbackSet.objects.filter(group=group)

    def add_comments_to_timeline(self, group, timeline):
        comments = self.viewclass._get_comments_for_group(group)
        for comment in comments:
            if comment.published_datetime not in timeline.keys():
                timeline[comment.published_datetime] = []

            if comment.feedback_set.feedbackset_type == group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY:
                comment_related_deadline = comment.feedback_set.group.assignment.first_deadline
            else:
                comment_related_deadline = comment.feedback_set.deadline_datetime

            timeline[comment.published_datetime].append({
                "type": "comment",
                "obj": comment,
                "related_deadline": comment_related_deadline
            })
        return timeline

    def add_announcements_to_timeline(self, group, feedbacksets, timeline):
        """
        TODO: document

        :param group:
        :param feedbacksets:
        :param timeline:
        :return:
        """
        if len(feedbacksets) == 0:
            return group.parentnode.first_deadline, timeline

        first_feedbackset = feedbacksets[0]
        # last_deadline = first_feedbackset.deadline_datetime
        last_deadline = None

        for index, feedbackset in enumerate(feedbacksets):
            if index == 0:
                if group.parentnode.first_deadline is not None:
                    deadline_datetime = group.parentnode.first_deadline
                    last_deadline = group.parentnode.first_deadline
                else:
                    deadline_datetime = feedbackset.deadline_datetime
            else:
                deadline_datetime = feedbackset.deadline_datetime
                last_deadline = feedbackset.deadline_datetime

            if deadline_datetime not in timeline.keys():
                timeline[deadline_datetime] = []

            if deadline_datetime is not None and deadline_datetime <= timezone.now():
                timeline[deadline_datetime].append({
                    "type": "deadline_expired"
                })

            if feedbackset.created_datetime not in timeline.keys():
                timeline[feedbackset.created_datetime] = []

            # Add available first_deadline, either assignment.first_deadline(if index is 0)
            # or
            # feedbackset.deadline_datetime
            if group.parentnode.first_deadline is not None and index == 0:
                if deadline_datetime <= group.parentnode.first_deadline:
                    timeline[feedbackset.created_datetime].append({
                        "type": "deadline_created",
                        "obj": group.parentnode.first_deadline,
                        "user": first_feedbackset.created_by
                    })
                    first_feedbackset = feedbackset
            elif feedbackset.deadline_datetime is not None:
                if deadline_datetime <= feedbackset.deadline_datetime:
                    timeline[feedbackset.created_datetime].append({
                        "type": "deadline_created",
                        "obj": feedbackset.deadline_datetime,
                        "user": feedbackset.created_by
                    })
                    first_feedbackset = feedbackset
            elif feedbackset is not feedbacksets[0]:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline_created",
                    "obj": deadline_datetime,
                    "user": feedbackset.created_by
                })

            if deadline_datetime is None or last_deadline is None:
                pass
            elif deadline_datetime > last_deadline:
                last_deadline = deadline_datetime

            if feedbackset.grading_published_datetime is not None:
                if feedbackset.grading_published_datetime not in timeline.keys():
                    timeline[feedbackset.grading_published_datetime] = []
                timeline[feedbackset.grading_published_datetime].append({
                    "type": "grade",
                    "obj": feedbackset.grading_points,
                #     "gradeform": grade_form.AdvancedGradeForm.render_viewable(
                #         grade_form.AdvancedGradeForm(),
                #         feedbackset.group.parentnode,
                #         feedbackset)
                })
            # print last_deadline
        return last_deadline, timeline

    def sort_timeline(self, timeline):
        """
        TODO: document

        :param timeline:
        :return:
        """
        def compare_timeline_items(a, b):
            datetime_a = a[0]
            datetime_b = b[0]
            if datetime_a is None:
                datetime_a = datetime.datetime(1970, 1, 1)
            if datetime_b is None:
                datetime_b = datetime.datetime(1970, 1, 1)
            return cmp(datetime_a, datetime_b)

        sorted_timeline = collections.OrderedDict(sorted(timeline.items(), compare_timeline_items))
        return sorted_timeline

    def build_timeline(self, group, feedbacksets):
        """
        TODO: document

        :param group:
        :param feedbacksets:
        :return:
        """
        timeline = {}
        timeline = self.add_comments_to_timeline(group, timeline)
        last_deadline, timeline = self.add_announcements_to_timeline(group, feedbacksets, timeline)
        timeline = self.sort_timeline(timeline)

        return last_deadline, timeline
