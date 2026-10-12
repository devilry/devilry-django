from builtins import object
from functools import update_wrapper

from django.urls import re_path

from .decorators import cradminview, has_access_to_cradmin_instance

#: The name of the app index view (the landing page for the app).
#: We do not enforce this, but we assume that each app has a
#: view with this name.
INDEXVIEW_NAME = "INDEX"


class Url(object):
    """
    Url is mostly the same as func:`django.conf.urls.url`.
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
                based on the app name and the :obj:`django_cradmin.crinstance.BaseCrAdminInstance.id`.
        """
        self.regex = regex
        self.view = view
        self.kwargs = kwargs
        self.name = name


class App(object):
    """
    A cradmin App.

    Added to a :class:`django_cradmin.crinstance.BaseCrAdminInstance`
    with :obj:`django_cradmin.crinstance.BaseCrAdminInstance.apps`.

    Attributes:
        appname (str): The name of the app.
        request (django.http.HttpRequest): Django request object for the current request.
        active_viewname (str): The name of the view we are currently rendering.
    """

    #: See :meth:`~.App.get_appurls`.
    appurls = []

    def __init__(self, appname, request, active_viewname):
        self.appname = appname
        self.request = request
        self.active_viewname = active_viewname

    def active_viewname_is_indexview(self):
        """
        Is the active viewname the app index view?

        Returns:
            bool: ``True`` if
        """
        return self.active_viewname == INDEXVIEW_NAME

    def is_crinstance_rolefrontpage_app(self):
        """
        Is this the :obj:`django_cradmin.crinstance.BaseCrAdminInstance.rolefrontpage_appname`

        Returns:
            bool: ``True`` if the appname of this app is the same as
            ``request.cradmin_instance.rolefrontpage_appname``.
        """
        return self.appname == self.request.cradmin_instance.rolefrontpage_appname

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
    def _wrap_view(cls, cradmin_instance_id, appname, view, viewname):
        def viewwrapper(request, *args, **kwargs):
            request.cradmin_app = cls(appname, request, active_viewname=viewname)
            return has_access_to_cradmin_instance(cradmin_instance_id, cradminview(view))(request, *args, **kwargs)

        # Take name and docstring from view
        update_wrapper(viewwrapper, view, updated=())

        return viewwrapper

    @classmethod
    def build_urls(cls, cradmin_instance_id, appname):
        """
        Used internally by :meth:`django_cradmin.crinstance.BaseCrAdminInstance.urls`
        to build urls for all views in the app.
        """
        urls = []
        for pattern in cls.get_appurls():
            urls.append(
                re_path(
                    pattern.regex,
                    cls._wrap_view(cradmin_instance_id, appname, pattern.view, pattern.name),
                    name="{}-{}-{}".format(cradmin_instance_id, appname, pattern.name),
                    kwargs=pattern.kwargs,
                )
            )
        return urls

    def add_breadcrumb_list_items(self, breadcrumb_item_list):
        """
        Add items to the breadcrumb item list.

        If you completely override the :meth:`.get_breadcrumb_item_list_renderable` method
        without calling super (or calling this method explicitly), this method will have no effect.

        Examples::

            Simple example::

                def add_breadcrumb_list_items(self, breadcrumb_item_list):
                    breadcrumb_item_list.append(url='#', label='Test')


        Args:
            breadcrumb_item_list (django_cradmin.crbreadcrumb.BreadcrumbItemList): The breadcrumb item list
                to add items to.

        .. seealso:: :doc:`/crbreadcrumb`
        """

    def get_breadcrumb_item_list_renderable(self):
        """
        Get a breadcrumb item list renderable common for all views within this app.

        By default, this just uses ``request.cradmin_instance.get_breadcrumb_item_list_renderable()``
        (see :meth:`django_cradmin.crinstance.BaseCrAdminInstance.get_breadcrumb_item_list_renderable`).

        You will normally only want to override this if you want to customize how breadcrumbs
        are rendered for the views in this app. If you just need to add items to the breadcrumb item
        list, override :meth:`.add_breadcrumb_list_items`.

        If you override this, remember that the breadcrumb item list from
        ``request.cradmin_instance.get_breadcrumb_item_list_renderable()``
        can be ``None``, so if you use that method you have to remember to handle this.


        Returns:
            django_cradmin.crbreadcrumb.BreadcrumbItemList: A breadcrumb item list renderable object
                or ``None``.

        .. seealso:: :doc:`/crbreadcrumb`
        """
        breadcrumb_item_list = self.request.cradmin_instance.get_breadcrumb_item_list_renderable()
        if breadcrumb_item_list is not None:
            self.add_breadcrumb_list_items(breadcrumb_item_list=breadcrumb_item_list)
        return breadcrumb_item_list

    @property
    def page_cover_bem_block(self):
        """
        Override the default page cover BEM block for all views in the app.

        Used by :func:`django_cradmin.templatetags.cradmin_tags.cradmin_page_cover_bem_block` for more details.

        See also: :meth:`django_cradmin.crinstance.BaseCrAdminInstance.page_cover_bem_block`.
        """
        return self.request.cradmin_instance.page_cover_bem_block
