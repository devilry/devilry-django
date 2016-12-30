

from devilry.devilry_api.feedbackset_download.views.feedbackset_download_base import BaseFeedbacksetView
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
from devilry.devilry_api.models import APIKey


class StudentFeedbacksetView(BaseFeedbacksetView):

    permission_classes = (StudentPermissionAPIKey, )
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, )

    def get_role_query_set(self):
        """
        Returns role queryset for student role

        Returns:
            :class:`~devilry_group.Feedbackset` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_student_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def get(self, request, content_id, *args, **kwargs):
        super(StudentFeedbacksetView, self).get(request, content_id, *args, **kwargs)

    get.__doc__ = BaseFeedbacksetView.get.__doc__
