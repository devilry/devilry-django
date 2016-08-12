from devilry.devilry_api.feedbackset.serializers import serializer_base
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetSerializerStudnet(serializer_base.FeedbacksetSerializerBase):

    devilry_role = 'student'
