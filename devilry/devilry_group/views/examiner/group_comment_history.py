# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp

from devilry.devilry_group.views.cradmin_comment_history import CommentHistoryView
from devilry.devilry_group import models as group_models


class ExaminerGroupCommentHistoryView(CommentHistoryView):
    def get_queryset_for_role(self, role):
        return group_models.GroupCommentEditHistory.objects\
            .exclude_private_comment_not_created_by_user(user=self.request.user)\
            .filter(group_comment_id=self.group_comment.id,
                    group_comment__feedback_set__group=self.request.cradmin_role)\
            .order_by('-edited_datetime')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^groupcomment-history/(?P<group_comment_id>\d+)$',
            ExaminerGroupCommentHistoryView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]