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

    def create(self, **data):
        """
        Create object from the input ``data``.

        Should return a representation of the created object.
        """
        raise UnsupportedHttpMethodError()

    def read(self, id):
        """
        Read and return the object identified by ``id``.
        """
        raise UnsupportedHttpMethodError()

    def update(self, id, **data):
        """
        Update object identified by ``id`` from the input ``data``.

        Should return a representation of the updated object.
        """
        raise UnsupportedHttpMethodError()

    def delete(self, id):
        """
        Delete the object identified by ``id``.
        """
        raise UnsupportedHttpMethodError()

    def list(self, **data):
        """
        List objects. Use data to provide the ability to limit the results.
        """
        raise UnsupportedHttpMethodError()

    def batch(self, create=[], update=[], delete=[]):
        """
        Create, update and/or delete many items in a single operation.

        The advantage of this approach over many create, update and delete requests are
        efficiency and the ability to do all operations in one transaction.
        """
        raise UnsupportedHttpMethodError()