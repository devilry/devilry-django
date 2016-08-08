from django.utils.timezone import datetime
from rest_framework import serializers

from django.utils.translation import ugettext_lazy
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers import serializer_base
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetModelSerializer(serializer_base.FeedbacksetModelSerializer):

    class Meta:
        model = FeedbackSet
        fields = [
            'id',
            'group',
            'created_datetime',
            'feedbackset_type',
            'is_last_in_group',
            'deadline_datetime',
        ]

    def validate(self, data):
        """
        Checks existence of required data and makes sure that any other data than group,
        deadline_datetime and feedbackset_type is ignored,
        rest of the data will be set automatically.

        Returns:
            dict with group and deadline_datetime
        """
        # checks existence
        if 'group' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing', 'group missing.'))
        if 'deadline_datetime' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing', 'deadline_datetime missing.'))
        if 'feedbackset_type' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing', 'feedbackset_type missing.'))

        # ignore any other data
        validated_data = dict()
        validated_data['group'] = data['group']
        validated_data['deadline_datetime'] = data['deadline_datetime']
        validated_data['feedbackset_type'] = data['feedbackset_type']
        return validated_data

    def validate_is_last_in_group(self, value):
        """
        Because of is_last_in_group and group is unique together,
        this is needed to pass validation.
        Later on before the model is created we will set the old
        feedbackset's is_last_in_group to false and the new to true

        Returns:
            ``False``
        """
        return False

    def validate_group(self, value):
        """
        Make sure that examiner is part of assignment group

        Returns:
            :class:`~core.AssignemntGroup`
        """
        assignment_group_queryset = AssignmentGroup.objects \
            .filter_examiner_has_access(user=self.context['request'].user) \
            .filter(id=value.id).distinct()
        if not assignment_group_queryset:
            raise serializers.ValidationError(ugettext_lazy('Access denied', 'Examiner not part of assignment group'))
        return value

    def validate_deadline_datetime(self, value):
        """
        Make sure that deadline is not in the past

        TODO: we could also check if the previous set deadline has expired
        Returns:
            datetime

        """
        if value < datetime.now():
            raise serializers.ValidationError(ugettext_lazy('Deadline must be in the future'))
        return value

    def validate_feedbackset_type(self, value):
        """
        TODO: validate that the previous set is first_attempt or new_attempt if
        value is new_attempt etc..
        Args:
            value:

        Returns:

        """
        return value

    def __set_is_last_in_group_false_in_previous_feedbackset(self, group):
        """
        Sets the attribute :obj:`~devilry_group.Feedbackset.is_last_in_group` for the previous
         feedbackset to False
        Args:
            group: :class:`~core.AssignmentGroup`
        """
        previous_feedback_set = FeedbackSet.objects.filter(group=group, is_last_in_group=True).first()
        if not previous_feedback_set:
            return
        previous_feedback_set.is_last_in_group = False
        previous_feedback_set.save()

    def create(self, validated_data):
        """
        Creates a new feedbackset

        Returns:
            :class:`~devilry_group.Feedbackset`

        """
        self.__set_is_last_in_group_false_in_previous_feedbackset(validated_data['group'])

        user = self.context['request'].user
        return FeedbackSet.objects.create(created_by=user,
                                          deadline_datetime=validated_data['deadline_datetime'],
                                          feedbackset_type=validated_data['feedbackset_type'],
                                          group=validated_data['group'])
