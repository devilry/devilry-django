class RestfulManager(object):
    def __init__(self):
        self.restapis = []

    def register(self, restapi):
        if not hasattr(restapi, 'create_rest_url'):
            raise ValueError('Requires the create_rest_url method on any class that can be decorated with RestfulManager.register')
        self.restapis.append(restapi)
        return restapi

    def create_rest_urls(self):
        """
        Create a list of django url objects for the restful apis registered
        with this manager.

        Typical usage in urls.py::
        """
        return [r.create_rest_url() for r in self.restapis]

    def __iter__(self):
        for restapi in self.restapis:
            yield restapi.create_rest_url()

    def __add__(self, urlpatterns):
        print dir(urlpatterns)
        return urlpatterns
