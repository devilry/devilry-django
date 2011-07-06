import urllib2
import json

from login import login


class RestfulError(Exception):
    """ Raised when the restful call returns a JSON data containing an
    errormsg. """

class HttpResponseBadRequest(RestfulError):
    """ Raised on HTTP ``400 Bad Request`` response. """

class HttpResponseUnauthorized(RestfulError):
    """ """

class HttpResponseForbidden(RestfulError):
    """ Raised on HTTP ``403 Forbidden`` response. """

class HttpResponseNotFound(RestfulError):
    """ Raised on HTTP ``404 Not Found`` response. """



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
    req.add_header('Cookie', logincookie)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        errordata = e.read()
        errmsg = json.loads(errordata)
        if e.code == 400:
            raise HttpResponseBadRequest(errmsg)
        elif e.code == 401:
            raise HttpResponseUnauthorized(errmsg)
        elif e.code == 403:
            raise HttpResponseForbidden(errmsg)
        elif e.code == 404:
            raise HttpResponseNotFound(errmsg)
        else:
            raise
    data = response.read()

    # Convert json to python
    json_data = json.loads(data)
    if "errormsg" in json_data:
        raise RestfulError(json_data['errormsg'])
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


if __name__ == "__main__":
    logincookie = login('http://localhost:8000/authenticate/login',
            username='grandma', password='test')

    restful_factory = RestfulFactory("http://localhost:8000/")
    node = restful_factory.make("administrator/restfulsimplifiednode/")
    period = restful_factory.make("administrator/restfulsimplifiedperiod/")

    print 'All nodes:'
    for x in node.search(limit=4, query=''):
        print '  ', x

    print
    print 'Read Node with id=1:'
    print '  ', node.read(1)

    print
    print 'Create a new node:'
    newnode = node.create(short_name='newly_created', long_name='Newly created')
    print '  ', newnode

    print
    print 'Update Node with id={0}:'.format(newnode['id'])
    print '  ', node.update(1, long_name='This has been updated', short_name='has_been_updated')


    print
    print 'Delete and re-read Node with id={0}:'.format(newnode['id'])
    node.delete(newnode['id'])
    try:
        node.read(1)
    except HttpResponseForbidden, e:
        print 'Node with id=1 could not be read (which should be correct since we just deleted it)'
