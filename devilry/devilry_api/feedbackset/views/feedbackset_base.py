from rest_framework.generics import mixins, GenericAPIView
from rest_framework.filters import OrderingFilter
from devilry.devilry_api.auth.authentication import TokenAuthentication


class FeedbacksetListViewBase(mixins.ListModelMixin,
                              GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    filter_backends = [OrderingFilter]

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_query_set(self):
        raise NotImplementedError()

    def get_queryset(self):
        queryset = self.get_role_query_set()

        id = self.request.query_params.get('id', None)
        assignment_group_id = self.request.query_params.get('assignment_group_id', None)
        if id:
            queryset = queryset.filter(id=id)
        if assignment_group_id:
            queryset = queryset.filter(group__id=assignment_group_id)

        return queryset

    def get(self, request, *args, **kwargs):
        """
        Gets a list of feedback sets

        ---
        parameters:
            - name: ordering
              required: false
              paramType: query
              type: String
              description: ordering
            - name: id
              required: false
              paramType: query
              type: String
              description: feedbackset id
            - name: assignment_group_id
              required: false
              paramType: query
              type: int
              description: assignment_group_id filter

        """
        return self.list(request, *args, **kwargs)
