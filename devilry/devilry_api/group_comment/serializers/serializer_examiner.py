
from devilry.devilry_api.group_comment.serializers import serializer_base


class GroupCommentSerializerExaminer(serializer_base.GroupCommentSerializerBase):
    devilry_role = 'examiner'
