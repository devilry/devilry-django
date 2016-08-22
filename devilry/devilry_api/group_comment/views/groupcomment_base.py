from rest_framework.generics import mixins, GenericAPIView
from rest_framework.filters import OrderingFilter
from devilry.devilry_api.auth.authentication import TokenAuthentication


class BaseGroupCommentView(mixins.ListModelMixin,
                           GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    filter_backends = [OrderingFilter]

    @property
    def permission_classes(self):
        """
        Permission classes required

        Example:
            permission_classes = (IsAuthenticated, )

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    @property
    def api_key_permissions(self):
        """
        Should be a list with API key permissions :class:`devilry_api.APIKey`.

        Example:
            api_key_permissions = (APIKey.STUDENT_PERMISSION_WRITE, APIKey.STUDENT_PERMISSION_READ)

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError(
            "please set api_key_permission example: "
            "api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)")

    def get_role_query_set(self):
        """
        Returns queryset for role (examiner, student etc...).

        should return a :class:`~apps.core.AssignmentGroup` queryset.

        Raises:
            :class:`NotImplementedError`

        """
        raise NotImplementedError()

    def get_queryset(self):
        """
        Checks query parameters and applies them if given.

        Returns:
            :class:`~devilry_group.GroupComment` queryset.

        """
        queryset = self.get_role_query_set()
        queryset = queryset.filter(feedback_set__id=self.kwargs['feedback_set'])

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
        return self.list(request, *args, **kwargs)
