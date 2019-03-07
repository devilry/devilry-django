# -*- coding: utf-8 -*-


from django.conf import settings
from django.http import Http404
from cradmin_legacy import crapp

from devilry.devilry_group.views.cradmin_comment_history import CommentHistoryView
from devilry.devilry_group import models as group_models


class StudentGroupCommentHistoryView(CommentHistoryView):
    def dispatch(self, request, *args, **kwargs):
        response = super(StudentGroupCommentHistoryView, self).dispatch(request=request, *args, **kwargs)
        if self.group_comment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
            raise Http404()
        return response

    def get_queryset_for_role(self, role):
        return group_models.GroupCommentEditHistory.objects \
            .filter(group_comment_id=self.group_comment.id,
                    visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                    group_comment__feedback_set__group=self.request.cradmin_role) \
            .order_by('-edited_datetime')

    def should_edit_history_be_rendered(self):
        should_render = super(StudentGroupCommentHistoryView, self).should_edit_history_be_rendered()
        if settings.DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY and should_render:
            return True
        if self.group_comment.user == self.request.user and should_render:
            return True
        return False


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^groupcomment-history/(?P<group_comment_id>\d+)$',
            StudentGroupCommentHistoryView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]