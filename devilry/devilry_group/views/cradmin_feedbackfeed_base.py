from django.views.generic import base
from devilry.devilry_group import models
import collections


class FeedbackFeedBaseView(base.TemplateView):
    template_name = "devilry_group/feedbackfeed.django.html"

    def _get_comments_for_group(self, group):
        raise NotImplementedError("Subclasses must implement _get_queryset_for_group!")

    def _get_feedbacksets_for_group(self, group):
        return models.FeedbackSet.objects.filter(group=group)

    def __add_comments_to_timeline(self, group, timeline):
        comments = self._get_comments_for_group(group)
        for comment in comments:
            if comment.published_datetime not in timeline.keys():
                timeline[comment.published_datetime] = []
            timeline[comment.published_datetime].append({
                "type": "comment",
                "obj": comment
            })
        return timeline

    def __add_announcements_to_timeline(self, group, timeline):
        feedbacksets = self._get_feedbacksets_for_group(group)
        if len(feedbacksets) == 0:
            return timeline
        first_deadline = feedbacksets[0].deadline_datetime
        last_deadline = first_deadline
        for feedbackset in feedbacksets[1:]:
            if feedbackset.created_datetime not in timeline.keys():
                timeline[feedbackset.created_datetime] = []
            if feedbackset.deadline_datetime < first_deadline:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline",
                    "obj": first_deadline
                })
                first_deadline = feedbackset.deadline_datetime
            else:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline",
                    "obj": feedbackset.deadline_datetime,
                    "user": feedbackset.created_by
                })
            if feedbackset.deadline_datetime > last_deadline:
                last_deadline = feedbackset.deadline_datetime

            if feedbackset.published_datetime is not None:
                if feedbackset.published_datetime not in timeline.keys():
                    timeline[feedbackset.published_datetime] = []
                timeline[feedbackset.published_datetime].append({
                    "type": "grade",
                    "obj": feedbackset.points
                })
        return last_deadline, timeline

    def __sort_timeline(self, timeline):
        sorted_timeline = collections.OrderedDict(sorted(timeline.items()))
        return sorted_timeline

    def __build_timeline(self, group):
        timeline = {}
        timeline = self.__add_comments_to_timeline(group, timeline)
        last_deadline, timeline = self.__add_announcements_to_timeline(group, timeline)
        timeline = self.__sort_timeline(timeline)

        return last_deadline, timeline

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period

        context['timeline'] = self.__build_timeline(self.request.cradmin_role)

        return context
