from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset_download.views.feedbackset_download_base import BaseFeedbacksetView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet


class ExaminerFeedbacksetView(BaseFeedbacksetView):

    permission_classes = (ExaminerPermissionAPIKey, )
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_READ, )

    def get_role_queryset(self):
        """
        Returns feedbackset queryset for examiner role

        Returns:
            :class:`~devilry_group.Feedbackset` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_examiner_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def get(self, request, content_id, *args, **kwargs):
        return super(ExaminerFeedbacksetView, self).get(request, content_id, *args, **kwargs)

    get.__doc__ = BaseFeedbacksetView.get.__doc__
