from django.test import Client
import json


class RestClient(Client):
    """
    Extends the ``django.test.Client`` with methods for the REST verbs and
    application/json.
    """
    def rest_post(self, url, data):
        response = self.post(url,
                             data=json.dumps(data),
                             content_type="application/json",
                             HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_put(self, url, data):
        response = self.put(url,
                            data=json.dumps(data),
                            content_type="application/json",
                            HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_get(self, url, **data):
        response = self.get(url,
                            data=data,
                            HTTP_ACCEPT="application/json")
        return json.loads(response.content), response

    def rest_delete(self, url):
        response = self.delete(url,
                               HTTP_ACCEPT="application/json")
        return json.loads(response.content), response
