from django.utils.translation import ugettext_lazy
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.group_comment.serializers import serializer_base
from devilry.devilry_group.models import GroupComment


class GroupCommentSerializerStudent(serializer_base.GroupCommentSerializerBase):
    devilry_role = 'student'

    def validate(self, data):
        """
        validate and ignore any other data

        Args:
            data: dictionary

        Returns:
            dictonary with validated_data

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
        return validated_data

    def validate_feedback_set(self, value):
        """
        Make sure that student has access to feedbackset
        Args:
            value: :obj:`~devilry_group.Feedbackset`

        Returns:
            :obj:`~devilry_group.Feedbackset`
        """
        try:
            AssignmentGroup.objects \
                .filter_student_has_access(user=self.context['request'].user) \
                .get(id=value.group.id)
        except AssignmentGroup.DoesNotExist:
            raise PermissionDenied('Access denied ' 'Student not part of assignment group')
        return value

    def create(self, validated_data):
        """
        Creates a new comment
        Args:
            validated_data: dictionary with validated data

        Returns:
            :obj:`~devilry_group.GroupComment`

        """
        return GroupComment.objects.create(visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                           user=self.context['request'].user,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                           **validated_data)
