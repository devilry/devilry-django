
from devilry.devilry_api.group_comment.serializers import serializer_base


class GroupCommentSerializerPeriodAdmin(serializer_base.GroupCommentSerializerBase):
    devilry_role = 'periodadmin'

