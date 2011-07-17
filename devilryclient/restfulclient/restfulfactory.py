import urllib2
import json
from errors import (HttpResponseNotFound, HttpResponseBadRequest,
                    HttpResponseUnauthorized, HttpResponseForbidden,
                    JsonDecodeError)
from login import get_session_cookie


class CrudsJsonRequest(urllib2.Request):
    """ A Request handler that can do HTTP POST, GET, PUT and DELETE, using the
    CRUD+S (create, read, update, delete, search) methology, and where data is encoded
    using JSON. """
    CRUDS_TO_HTTP_MAP = {'create': 'POST',
                         'read': 'GET',
                         'update': 'PUT',
                         'delete': 'DELETE',
                         'search': 'GET'}

    def __init__(self, url, crudsmethod, data):
        """
        :param url: The request URL.
        :param crudsmethod: One of: ``"create", "read", "update", "delete", "search"``.
        :param data: Python object which can be serialized using ``json.dumps(data)``.
        """
        urllib2.Request.__init__(self, url, json.dumps(data))
        self.crudsmethod = crudsmethod
        self.add_header('Accept', 'application/json')

    def get_method(self):
        return self.CRUDS_TO_HTTP_MAP[self.crudsmethod]


def call_restful_method(url, crudsmethod, restful_method_kwargs):
    # Fetch data from url
    req = CrudsJsonRequest(url, crudsmethod, restful_method_kwargs)

    logincookie = get_session_cookie()

    req.add_header('Cookie', logincookie)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        #errmsg = json.loads(errordata)
        if e.code == 400:
            raise HttpResponseBadRequest(e)
        elif e.code == 401:
            raise HttpResponseUnauthorized(e)
        elif e.code == 403:
            raise HttpResponseForbidden(e)
        elif e.code == 404:
            raise HttpResponseNotFound(e)
        else:
            raise
    data = response.read()

    # Convert json to python
    json_data = json.loads(data)
    if "errormsg" in json_data:
        raise JsonDecodeError(json_data['errormsg'])
    return json_data


class RestfulWrapper(object):
    def __init__(self, urlprefix, urlpath):
        self.url = urlprefix + urlpath

    def _url_with_id(self, id):
        return '{url}{id}'.format(url=self.url, id=id)

    def create(self, **kwargs):
        return call_restful_method(self.url, 'create', kwargs)

    def read(self, id, **kwargs):
        return call_restful_method(self._url_with_id(id), 'read', kwargs)

    def update(self, id, **kwargs):
        return call_restful_method(self._url_with_id(id), 'update', kwargs)

    def delete(self, id, **kwargs):
        return call_restful_method(self._url_with_id(id), 'delete', kwargs)

    def search(self, **kwargs):
        return call_restful_method(self.url, 'search', kwargs)


class RestfulFactory(object):
    def __init__(self, urlprefix):
        self.urlprefix = urlprefix

    def make(self, urlpath):
        return RestfulWrapper(self.urlprefix, urlpath)
