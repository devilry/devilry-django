# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.http import Http404
from django_cradmin import crapp
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilder.itemvalue import TitleDescription

from devilry.devilry_group import models as group_models


class GroupCommentEditHistoryValue(TitleDescription):
    valuealias = 'groupcomment_edit_history'

    def get_title(self):
        # return self.groupcomment_edit_history.edited_datetimes
        return 'Title'

    def get_description(self):
        # return self.groupcomment_edit_history.pre_edit_text
        return 'Description'


class CommentHistoryView(listbuilderview.ListView):
    template_name = 'devilry_group/comment_history.django.html'
    value_renderer_class = GroupCommentEditHistoryValue

    def dispatch(self, request, *args, **kwargs):
        if 'group_comment_id' not in kwargs:
            raise Http404()
        try:
            self.group_comment = group_models.GroupComment.objects.get(id=kwargs['group_comment_id'])
        except group_models.GroupComment.DoesNotExist:
            raise Http404()
        return super(CommentHistoryView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = group_models.GroupCommentEditHistory.objects \
            .filter(group_comment_id=self.group_comment.id,
                    group_comment__feedback_set__group=self.request.cradmin_role)
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super(CommentHistoryView, self).get_context_data()
        print context_data
        return context_data


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^groupcomment-history/(?P<group_comment_id>\d+)$',
            CommentHistoryView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
