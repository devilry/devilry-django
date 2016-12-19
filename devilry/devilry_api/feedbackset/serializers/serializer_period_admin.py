from devilry.devilry_api.feedbackset.serializers.serializer_examiner import FeedbacksetSerializerExaminer


class FeedbacksetSerializerPeriodAadmin(FeedbacksetSerializerExaminer):
    devilry_role = 'periodadmin'

    def validate_group_id(self, value):
        return value
