from django.test import Client
import json


class RestClient(Client):
    """
    Extends the ``django.test.Client`` with methods for the REST verbs and
    application/json.
    """

    def _load_json(self, content):
        if content.strip() == '':
            return None
        try:
            return json.loads(content)
        except ValueError, e:
            raise ValueError('{0}: {1}'.format(e, content))

    def rest_post(self, url, data):
        response = self.post(url,
                             data=json.dumps(data),
                             content_type="application/json",
                             HTTP_ACCEPT="application/json")
        return self._load_json(response.content), response

    def rest_put(self, url, data, **extra):
        response = self.put(url,
                            data=json.dumps(data),
                            content_type="application/json",
                            HTTP_ACCEPT="application/json",
                            **extra)
        return self._load_json(response.content), response

    def rest_get(self, url, **data):
        response = self.get(url,
                            data=data,
                            HTTP_ACCEPT="application/json")
        return self._load_json(response.content), response

    def rest_delete(self, url):
        response = self.delete(url,
                               HTTP_ACCEPT="application/json")
        return self._load_json(response.content), response
