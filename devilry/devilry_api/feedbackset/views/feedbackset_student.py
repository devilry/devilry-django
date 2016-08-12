from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers.serializer_student import FeedbacksetSerializerStudnet
from devilry.devilry_api.feedbackset.views.feedbackset_base import FeedbacksetListViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetListViewStudent(FeedbacksetListViewBase):
    permission_classes = (StudentPermissionAPIKey, )
    serializer_class = FeedbacksetSerializerStudnet
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)

    def get_role_query_set(self):
        assignment_group_queryset = AssignmentGroup.objects.filter_student_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetListViewStudent, self).get(request, *args, **kwargs)

    get.__doc__ = FeedbacksetListViewBase.get.__doc__
