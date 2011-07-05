from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import HttpResponseBadRequest
from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required

from serializers import serialize, SerializableResult


class RestfulView(View):
    """
    :class:`RestfulView` and the :func:`restful_api`-decorator is use in
    conjunction to create a RESTful web service with a CRUD+S interface.
    """

    @classmethod
    def create_rest_url(cls):
        """
        Create a ``django.conf.urls.defaults.url``-object for this view::

            r'^{urlprefix}/(?P<id>[a-zA-Z0-9]+)?$

        Where ``urlprefix`` is ``cls._meta.urlprefix`` documented in
        :func:`restful_api`.

        The name of the url is the ``cls._meta.urlname``, documented in
        :func:`restful_api`.

        The view is wrapped by :func:`django.contrib.auth.decorators.login_required`.
        """
        return url(r'^{urlprefix}/(?P<id>[a-zA-Z0-9]+)?$'.format(urlprefix=cls._meta.urlprefix),
            login_required(cls.as_view()),
            name=cls._meta.urlname)

    @classmethod
    def get_rest_url(cls, *args, **kwargs):
        return reverse(cls._meta.urlname, args=args, kwargs=kwargs)

    @serialize
    def get(self, request, **kwargs):
        """ Maps HTTP POST requests to the ``crud_read`` and ``crud_search``
        methods, which subclasses can implement. ``crud_read`` is called when
        ``id`` is in ``kwargs``."""
        if kwargs['id'] == None:
            del kwargs['id']
            if not hasattr(self, 'crud_search'):
                return SerializableResult(dict(
                    error='GET method with no identifier (search) is not supported.'),
                    httpresponsecls=HttpResponseBadRequest)
            return self.crud_search(request, **kwargs)
        else:
            if not hasattr(self, 'crud_read'):
                return SerializableResult(dict(
                    error='GET method with identifier (read) is not supported.'),
                    httpresponsecls=HttpResponseBadRequest)
            return self.crud_read(request, **kwargs)

    @serialize
    def post(self, request, id=None):
        """ Maps HTTP POST requests to the ``crud_create`` method, which subclasses
        can implement. """
        return self.crud_create(request)

    @serialize
    def put(self, request, id):
        """ Maps HTTP PUT requests to the ``crud_update`` method, which subclasses
        can implement. """
        return self.crud_update(request, id)

    @serialize
    def delete(self, request, id):
        """ Maps HTTP DELETE requests to the ``crud_delete`` method, which subclasses
        can implement. """
        return self.crud_delete(request, id)


