from urllib import urlencode
from devilry.rest.restview import RestView
from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


class RestBase(object):
    """
    Abstract superclass for RESTful APIs.
    """

    def __init__(self, apipath, apiversion):
        self.apipath = apipath
        self.apiversion = apiversion

    @classmethod
    def create_url(cls, apipath, apiversion):
        urlpattern = r'^(?P<id_and_suffix>[a-zA-Z-0-9_\.-]+)?$'.format(**vars())
        return url(urlpattern,
                   login_required(RestView.as_view(cls, apipath, apiversion)),
                   name=cls.get_urlname(apipath, apiversion))

    @classmethod
    def get_urlname(cls, apipath, apiversion):
        name = cls.__name__
        return '{apipath}-{apiversion}-{name}'.format(**vars())

    @staticmethod
    def reverse_url(restcls, apipath, apiversion, id=None, suffix=None):
        id_and_suffix = ""
        if id:
            id_and_suffix += id
        if suffix:
            id_and_suffix += "." + suffix
        return reverse(restcls.get_urlname(apipath, apiversion), args=[],
                       kwargs=dict(id_and_suffix=id_and_suffix))


    def geturl(self, id=None, params={}):
        url = RestBase.reverse_url(self.__class__, self.apipath, self.apiversion)
        if id != None:
            url += str(id)
        if params:
            url += '?{0}'.format(urlencode(params))
        return url

    def create(self, **data):
        """
        Create object from the input ``data``.

        Should return a representation of the created object.
        """
        raise NotImplementedError()

    def read(self, id, **data):
        """
        Read and return the object identified by ``id``.

        May use ``data`` to limit/customize the response, however it _must_ work without ``data``.
        """
        raise NotImplementedError()

    def update(self, id, **data):
        """
        Update object identified by ``id`` from the input ``data``.

        Should return a representation of the updated object.
        """
        raise NotImplementedError()

    def delete(self, id, **data):
        """
        Delete the object identified by ``id``.

        May use ``data`` to customize the behavior, however it _must_ work without ``data``.
        """
        raise NotImplementedError()

    def list(self, **data):
        """
        List objects. Use data to provide the ability to limit the results.
        """
        raise NotImplementedError()

    def batch(self, create=[], update=[], delete=[]):
        """
        Create, update and/or delete many items in a single operation.

        The advantage of this approach over many create, update and delete requests are
        efficiency and the ability to do all operations in one transaction.
        """
        raise NotImplementedError()