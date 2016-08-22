from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers.serializer_student import FeedbacksetSerializerStudnet
from devilry.devilry_api.feedbackset.views.feedbackset_base import BaseFeedbacksetView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetViewStudent(BaseFeedbacksetView):
    permission_classes = (StudentPermissionAPIKey, )
    serializer_class = FeedbacksetSerializerStudnet
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)

    def get_role_query_set(self):
        """
        Returns role queryset for student role

        Returns:
            :class:`~devilry_group.Feedbackset` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_student_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetViewStudent, self).get(request, *args, **kwargs)

    get.__doc__ = BaseFeedbacksetView.get.__doc__
