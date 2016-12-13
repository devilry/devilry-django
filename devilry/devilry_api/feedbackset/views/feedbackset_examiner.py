from django.utils.translation import ugettext_lazy
from rest_framework import exceptions
from rest_framework.generics import mixins

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers.serializer_examiner import FeedbacksetSerializerExaminer
from devilry.devilry_api.feedbackset.views.feedbackset_base import BaseFeedbacksetView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetViewExaminer(mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              BaseFeedbacksetView):
    permission_classes = (ExaminerPermissionAPIKey, )
    serializer_class = FeedbacksetSerializerExaminer

    #: examiner permissions allowed for view
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)

    def get_object(self):
        """

        Returns a :obj:`devilry_group.Feedbackset` with id passed in queryparams

        Returns:
            :obj:`devilry_group.Feedbackset`
        """
        id = self.request.query_params.get('id', None)
        if not id:
            raise exceptions.ParseError(ugettext_lazy('query parameter "id" required'))

        instance = self.get_queryset().first()
        if not instance:
            raise exceptions.NotFound(ugettext_lazy('Feedbackset with id: {} not found'.format(id)))
        return instance

    def get_role_query_set(self):
        """
        Returns role queryset for examiner role

        Returns:
            :class:`~devilry_group.Feedbackset` queryset
        """
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
            - name: group_id
              required: true
              paramType: form
              type: int
              description: Related assignment_group id
            - name: deadline_datetime
              required: true
              paramType: form
              type: DateTime
              description: Deadline
            - name: feedbackset_type
              required: true
              paramType: form
              enum:
                - new_attempt
                - re_edit
              description: feedbackset type

        """
        return super(FeedbacksetViewExaminer, self).create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Publish feedbackset

        grading_points is sent from query parameter, maybe should be in from?
        ---
        parameters:
            - name: id
              required: true
              paramType: query
              type: int
              description: id for feedbackset to publish
            - name: grading_points
              required: true
              paramType: query
              type: int
              description: points for feedbackset

        """
        return super(FeedbacksetViewExaminer, self).partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetViewExaminer, self).get(request, *args, **kwargs)

    get.__doc__ = BaseFeedbacksetView.get.__doc__
