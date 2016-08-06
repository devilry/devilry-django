from django.utils.timezone import datetime
from rest_framework import serializers

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
        print(data)
        return data

    def validate_group(self, value):
        assignment_group_queryset = AssignmentGroup.objects \
            .filter_examiner_has_access(user=self.context['request'].user) \
            .filter(id=value.id).distinct()
        if not assignment_group_queryset:
            raise serializers.ValidationError("Access denied, Examiner not part of assignment group")
        return value

    def validate_deadline_datetime(self, value):
        if value < datetime.now():
            raise serializers.ValidationError("Deadline must be in the future")
        return value

    def create(self, validated_data):
        print(validated_data)
