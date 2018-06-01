# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilder.itemvalue import TitleDescription

from devilry.apps.core.group_user_lookup import GroupUserLookup
from devilry.devilry_cradmin.devilry_listbuilder.feedbackfeed_timeline import StudentGroupCommentItemValueMinimal, \
    ExaminerGroupCommentItemValueMinimal, AdminGroupCommentItemValueMinimal
from devilry.devilry_group import models as group_models


class GroupCommentEditHistoryValue(TitleDescription):
    template_name = 'devilry_group/group_comment_history/history_item_value.django.html'
    valuealias = 'groupcomment_edit_history'

    def get_title(self):
        return self.groupcomment_edit_history.edited_datetime


class CommentHistoryView(listbuilderview.View):
    template_name = 'devilry_group/group_comment_history/comment_history.django.html'
    value_renderer_class = GroupCommentEditHistoryValue

    def get_pagetitle(self):
        return ugettext_lazy('Comment edit history')

    def get_pageheading(self):
        return ugettext_lazy('Comment edit history')

    def dispatch(self, request, *args, **kwargs):
        if 'group_comment_id' not in kwargs:
            raise Http404()
        try:
            self.group_comment = group_models.GroupComment.objects.get(id=kwargs['group_comment_id'])
        except group_models.GroupComment.DoesNotExist:
            raise Http404()
        return super(CommentHistoryView, self).dispatch(request, *args, **kwargs)

    def get_no_items_message(self):
        return ugettext_lazy('No items')

    def get_queryset_for_role(self, role):
        raise NotImplementedError()

    def get_current_group_comment_value_item_class(self):
        """
        Get the item value class for rendering the current group comment.
        """
        if self.group_comment.user_role == group_models.GroupComment.USER_ROLE_STUDENT:
            return StudentGroupCommentItemValueMinimal
        elif self.group_comment.user_role == group_models.GroupComment.USER_ROLE_EXAMINER:
            return ExaminerGroupCommentItemValueMinimal
        elif self.group_comment.user_role == group_models.GroupComment.USER_ROLE_ADMIN:
            return AdminGroupCommentItemValueMinimal
        raise ValueError('Unknown comment user role: {}'.format(self.group_comment.user_role))

    def get_current_group_comment_renderable(self):
        group = self.request.cradmin_role
        assignment = self.request.cradmin_role.parentnode
        devilry_viewrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        group_user_lookup = GroupUserLookup(
            group=group,
            assignment=assignment,
            requestuser=self.request.user,
            requestuser_devilryrole=devilry_viewrole)
        group_comment_value_item_class = self.get_current_group_comment_value_item_class()
        return self.get_frame_renderer_class()(
            inneritem=group_comment_value_item_class(
                value=self.group_comment,
                devilry_viewrole=devilry_viewrole,
                assignment=assignment,
                group_user_lookup=group_user_lookup
            )
        )

    def get_context_data(self, **kwargs):
        context = super(CommentHistoryView, self).get_context_data(**kwargs)
        context['group_comment_renderable'] = self.get_current_group_comment_renderable()
        return context
