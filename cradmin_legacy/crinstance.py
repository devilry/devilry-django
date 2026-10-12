from django.conf.urls import include
from django.urls import reverse, re_path
from django.shortcuts import render
from django.utils.html import format_html

from cradmin_legacy.decorators import has_access_to_cradmin_instance
from . import crapp
from .registry import cradmin_instance_registry
from .views import roleselect


def reverse_cradmin_url(instanceid, appname, roleid=None, viewname=crapp.INDEXVIEW_NAME, args=None, kwargs=None):
    """
    Reverse an URL within a cradmin instance.

    Usage is very similar to :func:`django.urls.reverse`,
    but you specify the cradmin instance, appname, roleid and viewname
    instead of the url-name

    Examples:

        Reverse the frontpage on an app::

            myapp_index_url = reverse_cradmin_url(
                instanceid='siteadmin',
                appname='myapp',
                roleid=site.id)

        Reverse a specific view within an app::

            myapp_add_url = reverse_cradmin_url(
                instanceid='siteadmin',
                appname='myapp',
                roleid=site.id,
                viewname='add')
    """
    if roleid:
        if args:
            args = [roleid] + list(args)
        else:
            if not kwargs:
                kwargs = {}
            kwargs["roleid"] = roleid
    urlname = f"{instanceid}-{appname}-{viewname}"
    return str(reverse(urlname, args=args, kwargs=kwargs))


class BaseCrAdminInstance:
    """
    Base class for a cradmin_legacy instance.

    You define a subclass of this to setup a cradmin_legacy instance.

    Attributes:
        request (HttpRequest): The current HttpRequest.
    """

    #: The ID of the cradmin instance. Must be unique for the Django
    #: instance/site. Must be a string.
    #: This is typically a short readable slug that describes what
    #: the cradmin instance does.
    #: You do not need to specify this except you need to communicate/link
    #: between cradmin instances.
    id = None

    #: The regex for matching the role id.
    #: Defaults to ``\d+``.
    roleid_regex = r"\d+"

    #: The menu class for this cradmin instance.
    menuclass = None

    #: The class defining the role for this cradmin instance.
    #: If you do not set this, the role system will not be used,
    #: which means that you will not get a value in ``request.cradmin_role``.
    roleclass = None

    #: The name of the app that the user should be redirected to
    #: after selecting a role. Subclasses MUST eighter specify
    #: this or override :meth:`rolefrontpage_url`.
    rolefrontpage_appname = None

    #: If this is ``True``, we do not prefix the urls of the
    #: :obj:`~BaseCrAdminInstance.rolefrontpage_appname` with the
    #: appname. This means that it is hosted on ``/baseurl/<roleid>/``
    #: instead of ``/baseurl/<roleid>/<appname>/``.
    #:
    #: If you couple this with setting :obj:`~.BaseCrAdminInstance.roleclass`
    #: to ``None``, the frontpage will be hosted directly on ``/baseurl/``.
    #:
    #: If you set this to ``True``, you have to be ensure that the urls of any views
    #: within the rolefrontpage app does crash any urls in any of the other apps.
    flatten_rolefrontpage_url = False

    #: Apps within the instance.
    #: Iterable of ``(appname, appclass)`` tuples where ``appname``
    #: is a slug for the app and ``appclass`` is a subclass of
    #: :class:`cradmin_legacy.crapp.App`.
    #: Can also be specified by overriding :meth:`.get_apps`.
    apps = []

    def __init__(self, request):
        """
        Parameters:
            request (HttpRequest): The current HttpRequest.
                Stored in :attr:`.request`.
        """
        self.request = request

    def get_cradmin_theme_path(self):
        """
        Return a path to a theme in the same format as :setting:`CRADMIN_LEGACY_THEME_PATH`,
        to use a custom theme for this instance.
        """
        return None

    def get_rolequeryset(self):
        """
        Get the roles for the authenticated user.

        You get the authenticated user from ``self.request.user``.
        """
        raise NotImplementedError()

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        """
        raise NotImplementedError()

    def get_descriptiontext_for_role(self, role):
        """
        Get a longer description for the given ``role``.

        This is never used directly on its own - it is just the default text
        used by :meth:`.get_descriptionhtml_for_role`. If you want
        HTML in your description, override :meth:`.get_descriptionhtml_for_role`
        instead.
        """
        return None

    def get_descriptionhtml_for_role(self, role):
        """
        Get a longer description for the given ``role``.
        This is always shown after/below :meth:`.get_titletext_for_role`.

        Defaults to :meth:`.get_descriptiontext_for_role` filtered to
        make it HTML safe and wrapped in a paragraph tag.
        """
        descriptiontext = self.get_descriptiontext_for_role(role)
        if descriptiontext:
            return format_html("<p>{}</p>", descriptiontext)
        else:
            return ""

    def get_roleid(self, role):
        """
        Get the ID for the given ``role``.
        """
        return role.pk

    def get_role_from_roleid(self, roleid):
        """
        Get the role for the given ``roleid``.

        Defaults to looking up a :obj:`roleclass` object where
        ``pk==roleid``.

        Returns:
            A role object or ``None``.
        """
        try:
            return self.roleclass.objects.get(pk=roleid)
        except self.roleclass.DoesNotExist:
            pass
        return None

    def invalid_roleid_response(self, roleid):
        """
        This is called whenever someone requests a role slug that does not exist
        (if :meth:.`get_role_from_roleid`) returns ``None``.

        Returns:
            django.http.HttpResponse: Defaults to rendering
                ``cradmin_legacy/invalid_roleid.django.html``.
        """
        return render(self.request, "cradmin_legacy/invalid_roleid.django.html", {"roleid": roleid})

    def get_role_from_rolequeryset(self, role):
        """
        Returns the given role extracted via the :meth:`.get_rolequeryset`
        queryset.

        Raises ObjectDoesNotExist if the role is not found in the queryset.
        """
        return self.get_rolequeryset().get(pk=role.pk)

    def missing_role_response(self, role):
        """
        This is called whenever someone requests a role that exists but that
        they do not have (where meth:`.get_role_from_rolequeryset` raises ``DoesNotExist``).

        Returns:
            django.http.HttpResponse: Defaults to rendering
                ``cradmin_legacy/missing_role.django.html``
        """
        return render(self.request, "cradmin_legacy/missing_role.django.html", {"role": role})

    def _get_menu(self):
        if not hasattr(self, "_menu"):
            menuclass = self.menuclass
            self._menu = menuclass(self)
        return self._menu

    def get_menu(self):
        """
        Get the navigation menu for the authenticated user.

        Parameters:
            user (Django User): The user requesting the menu.

        Returns:
            cradmin_legacy.crmenu.Menu: An instance of :obj:`~.BaseCrAdminInstance.menuclass` by default, but you can
            override this method to determine/create the menu dynamically.

        See Also:
            :class:`cradmin_legacy.crmenu.Menu`.
        """
        return self._get_menu()

    def reverse_url(self, appname, viewname, args=None, kwargs=None, roleid=None):
        """
        Reverse an URL within this cradmin instance.

        The advantage over using :func:`django.urls.reverse`
        is that you do not need to hardcode the id of the cradmin instance,
        and that the ``roleid`` is automatically added to args or kwargs
        (depending on which one you use to pass arguments to the url).

        Args:
            appname (str): The name of the app.
            viewname (str): The name of the view within the app.
            args (list): Args for the view
            kwargs (dict): Keyword args for the view.
            roleid: The roleid.
        """
        kwargs = {"instanceid": self.id, "appname": appname, "viewname": viewname, "args": args, "kwargs": kwargs}
        if self.roleclass:
            if roleid is None:
                roleid = self.get_roleid(self.request.cradmin_role)
            kwargs["roleid"] = roleid
        return reverse_cradmin_url(**kwargs)

    def appindex_url(self, appname, args=None, kwargs=None, roleid=None):
        """
        Reverse the url of the landing page for the given app.

        The landing page is the view named :obj:`cradmin_legacy.crapp.INDEXVIEW_NAME`.

        This would be the same as using :meth:`.reverse_url` with ``viewname=crapp.INDEXVIEW_NAME``.

        Args:
            appname (str): The name of the app.
            args (list): Args for the view
            kwargs (dict): Keyword args for the view.
            roleid: The roleid.
        """
        return str(self.reverse_url(appname, viewname=crapp.INDEXVIEW_NAME, roleid=roleid, args=args, kwargs=kwargs))

    def rolefrontpage_url(self, roleid=None):
        """
        Returns the URL that the user should be redirected to
        after selecting a role.
        """
        if self.roleclass:
            if roleid is None:
                roleid = self.get_roleid(self.request.cradmin_role)
        return self.appindex_url(self.rolefrontpage_appname, roleid=roleid)

    def get_instance_frontpage_url(self):
        """
        Return the URL of the instance frontpage view.

        See:
            :meth:`.get_instance_frontpage_url`.
        """
        if self.__class__.__no_role_and_flatten_rolefrontpage_url():
            return self.rolefrontpage_url()
        else:
            return reverse(f"{self.id}-frontpage")

    def roleselectview_url(self):
        """
        Deprecated, use :meth:`.get_instance_frontpage_url` instead.
        """
        return self.get_instance_frontpage_url()

    def get_common_http_headers(self):
        """
        Override this to set common HTTP headers for all views in the instance.

        Returns:
            A mapping object mapping HTTP header name to value. Returns
            empty dict by default.
        """
        return {}

    def has_access(self):
        """
        Check if the given user has access to this cradmin instance.

        Defaults to ``self.request.user.is_authenticated``, but you
        can override this.
        """
        return self.request.user.is_authenticated

    def get_foreignkeyselectview_url(self, model_class):
        """
        Get foreign key select view URL for the given model class.

        This can be used by foreign key select widgets to lookup a view
        for this model within the current instance.

        By default this returns ``None``, so you have to override this
        if you want to use it.

        Parameters:
            model_class: A ``django.db.models.Model`` subclass.
        """
        return None

    def get_manytomanyselectview_url(self, model_class):
        """
        Get many-to-many select view URL for the given model class.

        This can be used by many-to-many widgets,
        like :class:`cradmin_legacy.widgets.modelmultichoice.ModelMultiChoiceWidget`,
        to lookup a view for this model within the current instance.

        By default this returns ``None``, so you have to override this
        if you want to use it.

        Parameters:
            model_class: A ``django.db.models.Model`` subclass.
        """
        return None

    @classmethod
    def get_roleselect_view(cls):
        """
        The view for selecting role.

        Defaults to::

            from cradmin_legacy.views import roleselect
            from django.contrib.auth.decorators import login_required
            return login_required(roleselect.RoleSelectView.as_view())

        If you want to provide your own role select view, you can simply implement
        it here. Another option is to extend RoleSelectView and override the ``template_name``.

        Note:

            The name of the URL for this view is ``<cradmin instance id>-roleselect``,
            where ``<cradmin instance id>`` is :obj:`.id`. You can reverse the URL of
            this view with :meth:`.get_instance_frontpage_url`.
        """
        return has_access_to_cradmin_instance(roleselect.RoleSelectView.as_view())

    @classmethod
    def get_instance_frontpage_view(cls):
        if cls.roleclass:
            return cls.get_roleselect_view()
        else:
            raise NotImplementedError(
                "When you do not define a roleclass, you have to override get_instance_frontpage_view()"
            )

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        If you have more than one BaseCrAdminInstance in a single Django
        instance, you have to implement this classmethod on each of the
        instances to be able to lookup/detect the _current_ BaseCrAdminInstance.

        Parameters:
            urlpath: The url path (HttpRequest.path) to match against.

        Returns:
            ``True`` if the given urlpath is for a view within this CrAdmin instance.
        """
        raise NotImplementedError()

    @classmethod
    def get_apps(cls):
        """
        See :obj:`.apps`. Defaults to returning :obj:`.apps`, but can be overridden.
        """
        return cls.apps

    @classmethod
    def get_app_url(cls, appname, appclass):
        appurlpatterns = appclass.build_urls(cls.id, appname)
        flatten = cls.rolefrontpage_appname == appname and cls.flatten_rolefrontpage_url
        if cls.roleclass:
            if flatten:
                return re_path(fr"^(?P<roleid>{cls.roleid_regex})/", include(appurlpatterns))
            else:
                return re_path(fr"^(?P<roleid>{cls.roleid_regex})/{appname}/", include(appurlpatterns))

        else:
            if flatten:
                return re_path(r"^", include(appurlpatterns))
            else:
                return re_path(fr"^{appname}/", include(appurlpatterns))

    @classmethod
    def _get_app_urls(cls):
        urls = []
        for appname, appclass in cls.get_apps():
            urls.append(cls.get_app_url(appname=appname, appclass=appclass))
        return urls

    @classmethod
    def __no_role_and_flatten_rolefrontpage_url(cls):
        return cls.flatten_rolefrontpage_url and not cls.roleclass

    @classmethod
    def urls(cls):
        """
        Get the url patterns for the cradmin instance.
        """
        cradmin_instance_registry.add(cls)
        urls = cls._get_app_urls()
        if not cls.__no_role_and_flatten_rolefrontpage_url():
            urls.append(re_path("^$", cls.get_instance_frontpage_view(), name=f"{cls.id}-frontpage"))

        return urls

    def add_extra_instance_variables_to_request(self, request):
        """
        Override this method to add extra attributes to the request object
        for all views in this cradmin instance.

        This is called by the decorator that wraps all views within the instance.
        """
        pass
