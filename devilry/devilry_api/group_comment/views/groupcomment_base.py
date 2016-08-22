from rest_framework.generics import mixins, GenericAPIView
from rest_framework.filters import OrderingFilter
from devilry.devilry_api.auth.authentication import TokenAuthentication


class GroupCommentViewBase(mixins.ListModelMixin,
                           GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    filter_backends = [OrderingFilter]

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    @property
    def api_key_permissions(self):
        raise NotImplementedError(
            "please set api_key_permission example: "
            "api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)")

    def get_role_query_set(self):
        raise NotImplementedError()

    def get_queryset(self):
        queryset = self.get_role_query_set()
        queryset = queryset.filter(feedback_set__id=self.feedback_set)

        # feedback_set_id = self.request.query_params.get('feedback_set_id', None)
        id = self.request.query_params.get('id', None)
        if id:
            queryset = queryset.filter(id=id)

        return queryset

    def get(self, request, feedback_set, *args, **kwargs):
        """
        List comments

        ---
        parameters:
            - name: ordering
              required: false
              paramType: query
              type: String
              description: ordering
            - name: feedback_set
              required: true
              paramType: path
              type: Int
              description: feedbackset id
            - name: id
              required: false
              paramType: query
              type: Int
              description: group comment id

        """
        self.feedback_set = feedback_set
        return self.list(request, *args, **kwargs)
