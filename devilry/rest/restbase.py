from django.core.urlresolvers import reverse
from django.views.generic import View
from django.conf.urls.defaults import url

from error import UnsupportedHttpMethodError


class RestBase(object):
    supported_methods = "GET", "POST", "PUT", "DELETE"
    def crud_create(self, **data):
        raise UnsupportedHttpMethodError()

    def crud_read(self, id):
        raise UnsupportedHttpMethodError()

    def crud_update(self, id, **data):
        raise UnsupportedHttpMethodError()

    def crud_delete(self, id):
        raise UnsupportedHttpMethodError()

    def list(self, **data):
        raise UnsupportedHttpMethodError()