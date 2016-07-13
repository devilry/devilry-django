# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APIRequestFactory


class TestCaseMixin(object):
    route = None
    viewclass = None
    is_viewset = False

    def get_request(self, method,
                    requestuser=None,
                    format='json',
                    data=None,
                    queryparams='',
                    **kwargs):
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
