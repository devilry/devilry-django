from rest_framework.permissions import IsAuthenticated

READ_HTTP_METHODS = ['GET', 'HEAD', 'OPTIONS']
WRITE_HTTP_METHODS = ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE']


class BaseIsAuthenticatedAPIKey(IsAuthenticated):
    """
    Base permission class
    """

    def has_permission(self, request, view):
        self.apikey = request.apikey_token
        return super(BaseIsAuthenticatedAPIKey, self).has_permission(request, view) and self.apikey
