from rest_framework.generics import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from devilry.devilry_api.models import APIKey
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers.serializer_examiner import FeedbacksetModelSerializer
from devilry.devilry_api.feedbackset.views.feedbackset_base import FeedbacksetListViewBase
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet
from django.utils.translation import ugettext_lazy


class FeedbacksetListViewExaminer(mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  FeedbacksetListViewBase):
    permission_classes = (ExaminerPermissionAPIKey, )
    serializer_class = FeedbacksetModelSerializer

    #: examiner permissions allowed for view
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)

    def get_object(self):
        id = self.request.query_params.get('id', None)
        if not id:
            raise exceptions.ParseError(ugettext_lazy('query paramter "id" required'))

        instance = self.get_queryset().first()
        if not instance:
            raise exceptions.NotFound(ugettext_lazy('Feedbackset with id: {} not found'.format(id)))
        return instance

    def get_role_query_set(self):
        assignment_group_queryset = AssignmentGroup.objects.filter_examiner_has_access(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def post(self, request, *args, **kwargs):
        """
        Create a new feedbackset

        ---
        omit_parameters:
            - query
            - path
        parameter_strategy: replace
        parameters:
            - name: group
              required: true
              paramType: form
              type: int
              description: Related assignment_group id
            - name: deadline_datetime
              required: true
              paramType: form
              type: Choice
              description: Deadline
            - name: feedbackset_type
              required: true
              paramType: form
              enum:
                - new_attempt
                - re_edit
              description: feedbackset type

        """
        return super(FeedbacksetListViewExaminer, self).create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
            Publish feedbackset

            ---
            parameters:
                - name: id
                  required: true
                  paramType: query
                  type: int
                  description: id for feedbackset to publish

            """
        return super(FeedbacksetListViewExaminer, self).partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetListViewExaminer, self).get(request, *args, **kwargs)

    get.__doc__ = FeedbacksetListViewBase.get.__doc__
