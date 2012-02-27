"""
Utils that makes testing of ``devilry.rest`` apps easier.
"""
from django.test import Client
import json


def dummy_urlreverse(restcls, apipath, apiversion, id=None):
    return '{0}-{1}.{2}-{3}'.format(restcls.__name__, apipath, apiversion, id)

def isoformat_datetime(datetimeobj):
    """
    Convert a ``datetime.datetime`` object to the string format expected by
    :func:`.indata.isoformatted_datetime`.
    """
    return datetimeobj.strftime('%Y-%m-%dT%H:%M:%S')

class RestClient(Client):
    def rest_create(self, url, **params):
        response = self.post(url,
                             data=json.dumps(params),
                             content_type="application/json",
                             HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_update(self, url, id, **params):
        response = self.put(url + str(id),
                             data=json.dumps(params),
                             content_type="application/json",
                             HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_read(self, url, id, **params):
        response = self.get(url + str(id),
                            data=params,
                            HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_delete(self, url, id):
        response = self.delete(url + str(id),
                               HTTP_ACCEPT="application/json")
        return json.loads(response.content), response
