from rest_framework.generics import mixins

from devilry.devilry_api.models import APIKey
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers.serializer_examiner import FeedbacksetModelSerializer
from devilry.devilry_api.feedbackset.views.feedbackset_base import FeedbacksetListViewBase
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetListViewExaminer(mixins.CreateModelMixin,
                                  FeedbacksetListViewBase):
    permission_classes = (ExaminerPermissionAPIKey, )
    serializer_class = FeedbacksetModelSerializer

    #: examiner permissions allowed for view
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)

    def get_role_query_set(self):
        assignment_group_queryset = AssignmentGroup.objects.filter_examiner_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def post(self, request, *args, **kwargs):
        """
        Create a new feedbackset

        ---
        parameters:
            - name: group
              required: true
              paramType: form
              type: int
              description: Related assignment_group id
            - name: deadline_datetime
              required: true
              paramType: form
              type: Datetime
              description: Deadline

        """
        pass
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetListViewExaminer, self).get(request, *args, **kwargs)

    get.__doc__ = FeedbacksetListViewBase.get.__doc__
