from django.core.urlresolvers import reverse
from django.views.generic import View
from django.conf.urls.defaults import url

from error import UnsupportedHttpMethodError


class RestBase(object):
    """
    RESTful interface.

    :cvar supported_methods: Supported HTTP methods.
    """
    supported_methods = "GET", "POST", "PUT", "DELETE"

    def crud_create(self, **data):
        """
        Create object from the input ``data``.

        Should return a representation of the created object.
        """
        raise UnsupportedHttpMethodError()

    def crud_read(self, id):
        """
        Read and return the object identified by ``id``.
        """
        raise UnsupportedHttpMethodError()

    def crud_update(self, id, **data):
        """
        Update object identified by ``id`` from the input ``data``.

        Should return a representation of the updated object.
        """
        raise UnsupportedHttpMethodError()

    def crud_delete(self, id):
        """
        Delete the object identified by ``id``.
        """
        raise UnsupportedHttpMethodError()

    def list(self, **data):
        """
        List objects. Use data to provide the ability to limit the results.
        """
        raise UnsupportedHttpMethodError()