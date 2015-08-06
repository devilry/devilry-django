import datetime
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Button
from django.db.models.sql.datastructures import DateTime
from django import forms
from devilry.devilry_group import models
from django_cradmin.viewhelpers import create
import collections
from devilry.devilry_group.models import GroupComment
from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crapp
from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django_cradmin.crispylayouts import PrimarySubmit

class FeedbackFeedBaseView(create.CreateView):
    template_name = "devilry_group/feedbackfeed.django.html"

    # for cradmin CreateView
    model=GroupComment
    fields=["text"]

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

    def __add_announcements_to_timeline(self, feedbacksets, timeline):
        if len(feedbacksets) == 0:
            return timeline
        first_feedbackset = feedbacksets[0]
        last_deadline = first_feedbackset.deadline_datetime
        for feedbackset in feedbacksets[0:]:
            if feedbackset.deadline_datetime not in timeline.keys():
                timeline[feedbackset.deadline_datetime] = []
            timeline[feedbackset.deadline_datetime].append({
                "type": "deadline_expired"
            })
            if feedbackset.created_datetime not in timeline.keys():
                timeline[feedbackset.created_datetime] = []

            if feedbackset.deadline_datetime < first_feedbackset.deadline_datetime:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline_created",
                    "obj": first_feedbackset.deadline_datetime,
                    "user": first_feedbackset.created_by
                })
                first_feedbackset = feedbackset
            elif feedbackset is not feedbacksets[0]:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline_created",
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

    def __build_timeline(self, group, feedbacksets):
        timeline = {}
        timeline = self.__add_comments_to_timeline(group, timeline)
        last_deadline, timeline = self.__add_announcements_to_timeline(feedbacksets, timeline)
        timeline = self.__sort_timeline(timeline)

        return last_deadline, timeline

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period

        feedbacksets = self._get_feedbacksets_for_group(self.request.cradmin_role)
        context['last_deadline'], context['timeline'] = self.__build_timeline(self.request.cradmin_role, feedbacksets)
        context['feedbacksets'] = feedbacksets
        context['last_feedbackset'] = feedbacksets[0]
        context['current_date'] = datetime.datetime.now()

        return context

    submit_use_label = _('Post comment')

    def get_buttons(self):
        app = self.request.cradmin_app
        user = self.request.user
        if self.request.cradmin_role.is_candidate(user):
            return [Submit('add comment',
                           'Add comment',
                           css_class='btn btn-success')]
        elif self.request.cradmin_role.is_examiner(user):
            return [Submit('add comment for examiners',
                           'Add comment for examiners',
                           css_class='btn btn-primary'),
                    Submit('add public comment',
                           'Add public comment',
                           css_class='btn btn-primary'),
                    Submit('add comment',
                           'Add comment',
                           css_class='btn btn-primary')]


    # def get_field_layout(self):
    #     return [
    #             layout.Fieldset(
    #                 'Post comment',
    #                 'text',
    #             )
    #     ]

    def save_object(self, form, commit=True):
        print '\nsave object from form\n'

        object = form.save(commit=False)
        assignment_group = self.request.cradmin_role
        user = self.request.user
        time = datetime.datetime.now()

        object.user = user
        object.created_datetime = time
        object.published_datetime = time

        object.comment_type = 'groupcomment'
        object.feedback_set = assignment_group.feedbackset_set.latest('created_datetime')

        if assignment_group.is_candidate(user):
            object.user_role = 'student'
            object.instant_publish = True
            object.visible_for_students = True
            object.published_datetime = time

        elif assignment_group.is_examiner(user):
            object.user_role = 'examiner'
            object.instant_publish = True
            object.visible_for_students = True
            if object.instant_publish is True:
                object.published_datetime = time

        else:
            object.user_role = 'admin'
            object.instant_publish = True
            object.visible_for_students = True

        # print '\nComment object debug:\n'
        # print object.user
        # print object.text
        # print object.created_datetime
        # print object.published_datetime
        # print object.user_role
        # print object.comment_type
        # print object.feedback_set
        # print object.instant_publish
        # print object.visible_for_students

        # return
        if commit:
            object.save()
        return object



# class FeedbackFeedBaseView(base.TemplateView):
#     template_name = "devilry_group/feedbackfeed.django.html"
#
#     def _get_comments_for_group(self, group):
#         raise NotImplementedError("Subclasses must implement _get_queryset_for_group!")
#
#     def _get_feedbacksets_for_group(self, group):
#         return models.FeedbackSet.objects.filter(group=group)
#
#     def __add_comments_to_timeline(self, group, timeline):
#         comments = self._get_comments_for_group(group)
#         for comment in comments:
#             if comment.published_datetime not in timeline.keys():
#                 timeline[comment.published_datetime] = []
#             timeline[comment.published_datetime].append({
#                 "type": "comment",
#                 "obj": comment
#             })
#         return timeline
#
#     def __add_announcements_to_timeline(self, feedbacksets, timeline):
#         if len(feedbacksets) == 0:
#             return timeline
#         first_feedbackset = feedbacksets[0]
#         last_deadline = first_feedbackset.deadline_datetime
#         for feedbackset in feedbacksets[0:]:
#             if feedbackset.deadline_datetime not in timeline.keys():
#                 timeline[feedbackset.deadline_datetime] = []
#             timeline[feedbackset.deadline_datetime].append({
#                 "type": "deadline_expired"
#             })
#             if feedbackset.created_datetime not in timeline.keys():
#                 timeline[feedbackset.created_datetime] = []
#
#             if feedbackset.deadline_datetime < first_feedbackset.deadline_datetime:
#                 timeline[feedbackset.created_datetime].append({
#                     "type": "deadline_created",
#                     "obj": first_feedbackset.deadline_datetime,
#                     "user": first_feedbackset.created_by
#                 })
#                 first_feedbackset = feedbackset
#             elif feedbackset is not feedbacksets[0]:
#                 timeline[feedbackset.created_datetime].append({
#                     "type": "deadline_created",
#                     "obj": feedbackset.deadline_datetime,
#                     "user": feedbackset.created_by
#                 })
#             if feedbackset.deadline_datetime > last_deadline:
#                 last_deadline = feedbackset.deadline_datetime
#
#             if feedbackset.published_datetime is not None:
#                 if feedbackset.published_datetime not in timeline.keys():
#                     timeline[feedbackset.published_datetime] = []
#                 timeline[feedbackset.published_datetime].append({
#                     "type": "grade",
#                     "obj": feedbackset.points
#                 })
#         return last_deadline, timeline
#
#     def __sort_timeline(self, timeline):
#         sorted_timeline = collections.OrderedDict(sorted(timeline.items()))
#         return sorted_timeline
#
#     def __build_timeline(self, group, feedbacksets):
#         timeline = {}
#         timeline = self.__add_comments_to_timeline(group, timeline)
#         last_deadline, timeline = self.__add_announcements_to_timeline(feedbacksets, timeline)
#         timeline = self.__sort_timeline(timeline)
#
#         return last_deadline, timeline
#
#     def get_context_data(self, **kwargs):
#         context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
#         context['subject'] = self.request.cradmin_role.assignment.period.subject
#         context['assignment'] = self.request.cradmin_role.assignment
#         context['period'] = self.request.cradmin_role.assignment.period
#
#         feedbacksets = self._get_feedbacksets_for_group(self.request.cradmin_role)
#         context['last_deadline'], context['timeline'] = self.__build_timeline(self.request.cradmin_role, feedbacksets)
#         context['feedbacksets'] = feedbacksets
#         context['current_date'] = datetime.datetime.now()
#
#         return context
