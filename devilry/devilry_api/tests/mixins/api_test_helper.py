# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APIRequestFactory


class TestCaseMixin(object):
    """
    A mixin class that makes it easier to write tests for django rest framework views.

    """
    #: Url route
    route = ''

    #: Class of the view to test
    viewclass = None

    #: Set to True if the viewclass is a viewset
    is_viewset = False

    def get_request(self, method,
                    requestuser=None,
                    format='json',
                    data=None,
                    queryparams='',
                    apikey=None,
                    **kwargs):
        """
        Creates a request using :class:`~rest_framework.test.APIRequestFactory`

        Parameters:
            method: The http method (get, post, ...).
            requestuser: The request.user to use.
            format: The format
            data: The data to post, put or patch
            queryparams: Url parameters (?id=1...)
            apikey: The api key to use if the viewclass has TokenAuthentication
            **kwargs:

        """
        if self.viewclass is None:
            raise NotImplementedError('You must set the viewclass attribute on TestCase classes using TestCaseMixin.')
        if self.route is None:
            raise NotImplementedError('You must set the route attribute on TestCase classes using TestCaseMixin.')
        data = data or {}
        request = {
            'get': APIRequestFactory().get('{}{}'.format(self.route, queryparams), format=format),
            'delete': APIRequestFactory().delete('{}{}'.format(self.route, queryparams)),
            'put': APIRequestFactory().put('{}{}'.format(self.route, queryparams),
                                           data=data,
                                           format=format),
            'post': APIRequestFactory().post('{}{}'.format(self.route, queryparams),
                                             data=data,
                                             format=format),
            'patch': APIRequestFactory().patch('{}{}'.format(self.route, queryparams),
                                               data=data,
                                               format=format),
        }[method]
        if requestuser:
            request.user = requestuser
        if apikey:
            request.META['HTTP_AUTHORIZATION'] = 'Token {}'.format(apikey)
        return request, kwargs

    def create_admin_user(self):
        return mommy.make(settings.AUTH_USER_MODEL, is_superuser=True, is_active=True)

    def mock_delete_request(self, method='delete', **kwargs):
        request, viewkwargs = self.get_request('delete', **kwargs)
        if self.is_viewset:
            view = self.viewclass.as_view({'delete': method})
        else:
            view = self.viewclass.as_view()
        response = view(request, **viewkwargs)
        return response

    def mock_get_request(self, method='get', **kwargs):
        request, viewkwargs = self.get_request('get', **kwargs)
        if self.is_viewset:
            view = self.viewclass.as_view({'get': method})
        else:
            view = self.viewclass.as_view()
        response = view(request, **viewkwargs)
        return response

    def mock_put_request(self, method='put', **kwargs):
        request, viewkwargs = self.get_request('put', **kwargs)
        if self.is_viewset:
            view = self.viewclass.as_view({'put': method})
        else:
            view = self.viewclass.as_view()
        response = view(request, **viewkwargs)
        return response

    def mock_patch_request(self, method='patch', **kwargs):
        request, viewkwargs = self.get_request('patch', **kwargs)
        if self.is_viewset:
            view = self.viewclass.as_view({'patch': method})
        else:
            view = self.viewclass.as_view()
        response = view(request, **viewkwargs)
        return response

    def mock_post_request(self, method='post', **kwargs):
        request, viewkwargs = self.get_request('post', **kwargs)
        if self.is_viewset:
            view = self.viewclass.as_view({'post': method})
        else:
            view = self.viewclass.as_view()
        response = view(request, **viewkwargs)
        return response
