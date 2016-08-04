from devilry.devilry_api.feedbackset.serializers import serializer_base
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetModelSerializer(serializer_base.FeedbacksetModelSerializer):

    class Meta:
        model = FeedbackSet
        fields = [
            'id',
            'assignment_group_id',
            'created_datetime',
            'feedbackset_type',
            'is_last_in_group',
            'deadline_datetime',
        ]
