from django.http import HttpResponse


class HttpJsonResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json; encoding=utf-8'
        super(HttpJsonResponse, self).__init__(*args, **kwargs)

class HttpXmlResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'text/xml; encoding=utf-8'
        super(HttpJsonResponse, self).__init__(*args, **kwargs)
