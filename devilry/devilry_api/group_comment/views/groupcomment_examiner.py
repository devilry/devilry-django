from rest_framework.generics import mixins

from devilry.devilry_api.group_comment.serializers.serializer_examiner import GroupCommentSerializerExaminer
from devilry.devilry_api.group_comment.views.groupcomment_base import BaseGroupCommentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import GroupComment
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.utils.translation import ugettext_lazy


class GroupCommentViewExaminer(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               BaseGroupCommentView):
    permission_classes = (ExaminerPermissionAPIKey, )
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_READ, APIKey.EXAMINER_PERMISSION_WRITE)
    serializer_class = GroupCommentSerializerExaminer

    def get_object(self):
        """
        This is only used to get a drafted comment

        Returns:
            :obj:`devilry_group.GroupComment`
        """
        if 'feedback_set' not in self.kwargs:
            raise ValidationError(ugettext_lazy('Url path parameter feedback_set required'))
        id = self.request.query_params.get('id', None)
        if not id:
            raise ValidationError(ugettext_lazy('Queryparam id required.'))
        try:
            comment = self.get_role_query_set().get(feedback_set__id=self.kwargs['feedback_set'], id=id)
        except GroupComment.DoesNotExist:
            raise NotFound
        if comment.feedback_set.grading_published_datetime is not None:
            raise PermissionDenied(ugettext_lazy('Cannot delete published comment.'))
        if comment.visibility != GroupComment.VISIBILITY_PRIVATE:
            raise PermissionDenied(ugettext_lazy('Cannot delete a comment that is not private.'))
        if not comment.part_of_grading:
            raise PermissionDenied(ugettext_lazy('Cannot delete a comment that is not a draft.'))
        return comment

    def get_role_query_set(self):
        """
        Returns role queryset for examiner role

        Returns:
            :class:`~devilry_group.GroupComment` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_examiner_has_access(user=self.request.user)
        return GroupComment.objects.filter(feedback_set__group=assignment_group_queryset,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT) \
            .exclude_private_comments_from_other_users(user=self.request.user)

    def get(self, request, feedback_set, *args, **kwargs):
        return super(GroupCommentViewExaminer, self).get(request, feedback_set, *args, **kwargs)

    get.__doc__ = BaseGroupCommentView.get.__doc__

    def post(self, request, feedback_set, *args, **kwargs):
        """
        post a comment to a feedbackset

        ---
        parameters:
            - name: feedback_set
              required: true
              paramType: path
              type: Int
              description: feedbackset id
            - name: text
              paramType: form
              required: true
              type: String
              description: comment text
            - name: part_of_grading
              required: false
              paramType: form
              type: Boolean
              description: part of grading
            - name: visibility
              required: false
              paramType: form
              enum:
                - visible-to-everyone
                - visible-to-examiner-and-admins
                - private
              description: comment visibility
        """
        request.data['feedback_set'] = feedback_set
        request.data['user_role'] = GroupComment.USER_ROLE_EXAMINER
        return super(GroupCommentViewExaminer, self).create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        destroy drafted comment

        ---
        parameters:
            - name: feedback_set
              required: true
              paramType: path
              type: Int
              description: feedbackset id
            - name: id
              required: true
              paramType: query
              type: Int
              description: comment id to destroy

        """
        return super(GroupCommentViewExaminer, self).destroy(request, *args, **kwargs)
