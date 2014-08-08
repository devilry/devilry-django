class RestfulManager(object):
    """
    The RestfulManager is used to simplify setting up URLs for (big) restful
    APIs.

    Basically, you create a ``RestfulManager``-object, lets call it
    ``myrestapi``, in you restful api, and decorate all your
    :class:`devilry.restful.RestfulView` classes with ``@myrestapi.register``.

    You can then add the urls by adding them to a
    ``django.conf.urls.patterns``-object like so::

        urlpatterns = patterns('devilry.apps.myexample')
        urlpatterns += myrestapi

    An alternative would be to not decorate your views using this class,
    and rather use :meth:`devilry.restful.RestfulView.create_rest_url`.
    """
    def __init__(self):
        self._restapis = []

    def register(self, restapi):
        """
        Register the given ``restapi`` with the manager.

        :param restapi: A subclass of :class:`devilry.restful.RestfulView`.
        """
        if not hasattr(restapi, 'create_rest_url'):
            raise ValueError('Requires the create_rest_url method on any class that can be decorated with RestfulManager.register')
        self._restapis.append(restapi)
        return restapi

    def __iter__(self):
        """ Iterate over all urls in the registered restful apis. This is what makes
        ``urlpattern += myrestfulmanager`` work. """
        for restapi in self._restapis:
            yield restapi.create_rest_url()

    def iter_restfulclasses(self):
        """
        Iterate over the registered RESTful API classes and yield each API class.
        """
        return self._restapis.__iter__()
