from django.utils.translation import ugettext_lazy
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


from devilry.devilry_api.group_comment.serializers import serializer_base
from devilry.devilry_group.models import GroupComment
from devilry.apps.core.models import AssignmentGroup


class GroupCommentSerializerPeriodAdmin(serializer_base.GroupCommentSerializerBase):
    devilry_role = 'periodadmin'

    def validate(self, data):
        """
        validate data and ignore any other data

        Args:
            data: request data

        Raises:
            :class:`~rest_framework.serializers.ValidationError`

        Returns:
            dictionary with validated data
        """
        if 'text' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'text missing.'))
        if 'feedback_set' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'feedback_set missing.'))

        # ignore any other data
        validated_data = dict()
        validated_data['text'] = data['text']
        validated_data['feedback_set'] = data['feedback_set']
        validated_data['user_role'] = data['user_role']
        if 'visibility' not in data:
            validated_data['visibility'] = GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
        else:
            validated_data['visibility'] = data['visibility']

        if (validated_data['visibility'] == GroupComment.VISIBILITY_PRIVATE or
                'part_of_grading' in data and data['part_of_grading']):
            raise serializers.ValidationError(ugettext_lazy('Period admin cannot post part of grading comments'))

        validated_data['part_of_grading'] = False
        return validated_data

    def validate_feedback_set(self, value):
        """
        Make sure that period admin has access to feedbackset

        Args:
            value: :obj:`~devilry_group.FeedbackSet`

        Raises:
            :class:`~rest_framework.exceptions.PermissionDenied`

        Returns:
            :obj:`~devilry_group.FeedbackSet`
        """
        try:
            AssignmentGroup.objects \
                .filter_user_is_period_admin(self.context['request'].user) \
                .get(id=value.group.id)
        except AssignmentGroup.DoesNotExist:
            raise PermissionDenied('Access denied Period admin does not have access to feedbackset')
        return value

    def create(self, validated_data):
        """
        Creates a new comment
        Args:
            validated_data: dictionary with validated data

        Returns:
            :obj:`~devilry_group.GroupComment`
        """
        return GroupComment.objects.create(user=self.context['request'].user,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                           **validated_data)
