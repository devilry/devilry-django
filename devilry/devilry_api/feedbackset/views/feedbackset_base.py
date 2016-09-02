from rest_framework.generics import mixins, GenericAPIView
from rest_framework.filters import OrderingFilter
from devilry.devilry_api.auth.authentication import TokenAuthentication


class BaseFeedbacksetView(mixins.ListModelMixin,
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
            api_key_permissions = (:attr:`APIKey.STUDENT_PERMISSION_WRITE`, :attr:`APIKey.STUDENT_PERMISSION_READ`)

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
            :class:`~devilry_group.Feedbackset` queryset.

        """
        queryset = self.get_role_query_set()

        id = self.request.query_params.get('id', None)
        group_id = self.request.query_params.get('group_id', None)
        if id:
            queryset = queryset.filter(id=id)
        if group_id:
            queryset = queryset.filter(group__id=group_id)

        return queryset

    def get(self, request, *args, **kwargs):
        """
        Get a list of feedback sets

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
            - name: group_id
              required: false
              paramType: query
              type: int
              description: assignment_group_id filter

        """
        return self.list(request, *args, **kwargs)
