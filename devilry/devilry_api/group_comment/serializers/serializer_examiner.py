from django.utils.translation import ugettext_lazy
from rest_framework import serializers

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.group_comment.serializers import serializer_base
from devilry.devilry_group.models import GroupComment
from devilry.devilry_group.models import FeedbackSet


class GroupCommentSerializerExaminer(serializer_base.GroupCommentSerializerBase):
    devilry_role = 'examiner'

    def validate(self, data):
        """
        validate data and ignore any other data
        Args:
            data:

        Returns:

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
        if 'part_of_grading' not in data:
            validated_data['part_of_grading'] = False
        else:
            validated_data['part_of_grading'] = data['part_of_grading']
        return validated_data

    def validate_feedback_set(self, value):
        """
        Make sure that examiner has access to feedbackset
        Args:
            value: :obj:`~devilry_group.Feedbackset`

        Returns:
            :obj:`~devilry_group.Feedbackset`

        """
        try:
            AssignmentGroup.objects \
                .filter_examiner_has_access(self.context['request'].user) \
                .get(id=value.group.id)
        except AssignmentGroup.DoesNotExist:
            raise serializers.ValidationError('Access denied ' 'Examiner not part of assignment group')
        return value

    def validate_part_of_grading(self, value):
        """
        If value is true then visibility has to be private and
        comment cannot be part of grading of feedbackset grading is published
        Args:
            value: :attr:`~devilry_group.GroupComment.part_of_grading`

        Returns:
            :attr:`~devilry_group.GroupComment.part_of_grading`
        """
        if value and ('visibility' not in self.context['request'].data or
                        self.context['request'].data['visibility'] != GroupComment.VISIBILITY_PRIVATE):
            raise serializers.ValidationError(ugettext_lazy('if part_of_grading = True, visibility has to be private'))
        feedback_set = FeedbackSet.objects.get(id=self.context['request'].data['feedback_set'])
        if value and feedback_set.grading_published_datetime is not None:
            raise serializers.ValidationError(ugettext_lazy('Cannot post part of grading comment '
                                                            'when grading is published'))

        return value

    def validate_visibility(self, value):
        """
        If value is private, then part of grading has to be ``True``
        Args:
            value: :attr:`~devilry_group.GroupComment.visibility`

        Returns:
            :attr:`~devilry_group.GroupComment.visibility`

        """
        if value == GroupComment.VISIBILITY_PRIVATE and ('part_of_grading' not in self.context['request'].data or
                                                             not self.context['request'].data['part_of_grading']):
            raise serializers.ValidationError(ugettext_lazy('if visibility = private, part_of_grading has to be True'))
        return value

    def create(self, validated_data):
        """
        Creates a new comment
        Args:
            validated_data: dictionary with validated data

        Returns:
            :obj:`~devilry_group.GroupComment

        """
        return GroupComment.objects.create(user=self.context['request'].user,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                           **validated_data)
