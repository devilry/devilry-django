from devilry.devilry_api.feedbackset.serializers import serializer_base


class FeedbacksetSerializerStudnet(serializer_base.BaseFeedbacksetSerializer):

    devilry_role = 'student'
