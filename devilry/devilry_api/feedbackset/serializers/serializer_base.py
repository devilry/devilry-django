from rest_framework import serializers


class FeedbacksetModelSerializer(serializers.ModelSerializer):
    """
    Feedbackset model serializer for :class:`~devilry_group.FeedbackSet`
    """

    #: Assignment group id that owns this feedbackset.
    assignment_group_id = serializers.SerializerMethodField()

    def get_assignment_group_id(self, instance):
        return instance.group.id
