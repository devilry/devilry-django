from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APIRequestFactory, force_authenticate


class ApiTestMixin:
    """
    Mixin class for API tests.

    Can be used for ViewSets too. Just override :meth:`.get_as_view_kwargs` - se example in the docs
    for that method.
    """
    apiview_class = None

    def get_default_requestuser(self):
        return None

    def make_user(self, shortname='user@example.com', **kwargs):
        return mommy.make(settings.AUTH_USER_MODEL, shortname=shortname, **kwargs)

    def make_superuser(self, shortname='super@example.com', **kwargs):
        return self.make_user(shortname=shortname, is_superuser=True, **kwargs)

    def get_as_view_kwargs(self):
        """
        The kwargs for the ``as_view()``-method of the API view class.

        If you are writing tests for a ViewSet, you have to override this
        to define what action you are testing (list, retrieve, update, ...), like this::

            def get_as_view_kwargs(self):
                return {
                    'get': 'list'
                }
        """
        return {}

    def add_authenticated_user_to_request(self, request, requestuser):
        if requestuser:
            force_authenticate(request, requestuser)

    def make_request(self, method, viewkwargs=None, api_url='/test/', data=None, requestuser=None):
        factory = APIRequestFactory()
        request = getattr(factory, method)(api_url, format='json', data=data)
        viewkwargs = viewkwargs or {}
        if requestuser:
            request.user = requestuser or self.get_default_requestuser()
        response = self.apiview_class.as_view(**self.get_as_view_kwargs())(request, **viewkwargs)
        response.render()
        return response

    def make_get_request(self, viewkwargs=None, api_url='/test/', data=None, requestuser=None):
        return self.make_request(method='get', viewkwargs=viewkwargs,
                                 api_url=api_url, data=data,
                                 requestuser=requestuser)

    def make_post_request(self, viewkwargs=None, api_url='/test/', data=None, requestuser=None):
        return self.make_request(method='post', viewkwargs=viewkwargs,
                                 api_url=api_url, data=data,
                                 requestuser=requestuser)

    def make_put_request(self, viewkwargs=None, api_url='/test/', data=None, requestuser=None):
        return self.make_request(method='put', viewkwargs=viewkwargs,
                                 api_url=api_url, data=data,
                                 requestuser=requestuser)

    def make_delete_request(self, viewkwargs=None, api_url='/test/', data=None, requestuser=None):
        return self.make_request(method='delete', viewkwargs=viewkwargs,
                                 api_url=api_url, data=data,
                                 requestuser=requestuser)
