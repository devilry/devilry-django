import urllib2
import json

from login import login
from utils import dict_to_http_querystring


class RestfulError(Exception):
    """ Raised when the restful call returns a JSON data containing an
    errormsg. """

class RestfulInvalidParameterError(RestfulError):
    """ """

class RestfulUnauthorizedError(RestfulError):
    """ """

class RestfulForbiddenError(RestfulError):
    """ """

class RestfulNotFoundError(RestfulError):
    """ """


def call_restful_method(url, **kwargs):
    # Create url
    querystring = dict_to_http_querystring(kwargs)
    full_url = "%s?%s" % (url, querystring)

    # Fetch data from url
    req = urllib2.Request(full_url)
    req.add_header('Cookie', logincookie)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        errmsg = e.read()
        if e.code == 400:
            raise RestfulInvalidParameterError(errmsg)
        elif e.code == 401:
            raise RestfulUnauthorizedError(errmsg)
        elif e.code == 403:
            raise RestfulForbiddenError(errmsg)
        elif e.code == 404:
            raise RestfulNotFoundError(errmsg)
        else:
            raise
    data = response.read()

    # Convert json to python
    json_data = json.loads(data)
    if "errormsg" in json_data:
        raise RestfulError(json_data['errormsg'])
    return json_data


class RestfulFactory(object):
    def __init__(self, urlprefix):
        self.urlprefix = urlprefix

    def create_get(self, urlpath):
        url = self.urlprefix + urlpath
        def restfunc(**kwargs):
            return call_restful_method(url, **kwargs)
        return restfunc


if __name__ == "__main__":
    logincookie = login('http://localhost:8000/ui/login',
            username='examiner0', password='test')

    #from devilry.restful_client.restful.examiner import assignments
    restful_factory = RestfulFactory("http://localhost:8000/")
    assignments = restful_factory.create_get("restful/examiner/assignments/")
    for x in assignments(limit=4, query='1100')['items']:
        print x
