from devilry.devilry_api.feedbackset.serializers import serializer_base


class FeedbacksetSerializerStudnet(serializer_base.FeedbacksetSerializerBase):

    devilry_role = 'student'
