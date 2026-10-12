from functools import update_wrapper

from django.urls import re_path

from .decorators import cradminview, has_access_to_cradmin_instance

#: The name of the app index view (the landing page for the app).
#: We do not enforce this, but we assume that each app has a
#: view with this name.
INDEXVIEW_NAME = "INDEX"


class Url:
    """
    Url is mostly the same as func:`django.urls.re_path`.
    You use Url to add urls to an app.
    """

    def __init__(self, regex, view, kwargs=None, name=None):
        """
        Args:
            regex: The URL regex.
            view: The view (E.g.: ``MyView.as_view()``).
            kwargs: Keyword arguments for the view.
            name: The name of the view. This just have to be unique within
                the :class:`.App` - the actual URL name is generated
                based on the app name and the :obj:`cradmin_legacy.crinstance.BaseCrAdminInstance.id`.
        """
        self.regex = regex
        self.view = view
        self.kwargs = kwargs
        self.name = name


class App:
    """
    A cradmin App.

    Added to a :class:`cradmin_legacy.crinstance.BaseCrAdminInstance`
    with :obj:`cradmin_legacy.crinstance.BaseCrAdminInstance.apps`.
    """

    #: See :meth:`~.App.get_appurls`.
    appurls = []

    def __init__(self, appname, request, active_viewname):
        self.appname = appname
        self.request = request
        self.active_viewname = active_viewname

    def reverse_appurl(self, viewname, args=None, kwargs=None):
        """
        Works just like :func:`django.urls.reverse`, except
        that the name is the name given in :obj:`.appurls`, not the full
        name of the URL.

        This means that you should use this to reverse urls within this app.
        """
        return self.request.cradmin_instance.reverse_url(
            appname=self.appname, viewname=viewname, args=args, kwargs=kwargs
        )

    def reverse_appindexurl(self, args=None, kwargs=None):
        """
        Shortcut for::

            reverse_appurl(crapp.INDEXVIEW_NAME, args=args, kwargs=kwargs)
        """
        return self.reverse_appurl(viewname=INDEXVIEW_NAME, args=args, kwargs=kwargs)

    @classmethod
    def get_appurls(cls):
        """
        Get app URLs. Defaults to :obj:`~.App.appurls`.

        Returns:
            A list of :class:`.Url` objects.
        """
        return cls.appurls

    @classmethod
    def _wrap_view(cls, appname, view, viewname):
        def viewwrapper(request, *args, **kwargs):
            request.cradmin_app = cls(appname, request, active_viewname=viewname)
            return has_access_to_cradmin_instance(cradminview(view))(request, *args, **kwargs)

        # Take name and docstring from view
        update_wrapper(viewwrapper, view, updated=())

        return viewwrapper

    @classmethod
    def build_urls(cls, cradmin_instance_id, appname):
        """
        Used internally by :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.urls`
        to build urls for all views in the app.
        """
        urls = []
        for pattern in cls.get_appurls():
            urls.append(
                re_path(
                    pattern.regex,
                    cls._wrap_view(appname, pattern.view, pattern.name),
                    name=f"{cradmin_instance_id}-{appname}-{pattern.name}",
                    kwargs=pattern.kwargs,
                )
            )
        return urls
