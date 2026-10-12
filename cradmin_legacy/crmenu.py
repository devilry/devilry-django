from django.template.loader import render_to_string
import warnings


class MenuItem:
    """
    A  menu item. Basically a pythonic interface to
    create a HTML element.

    If you want to make major changes to the look and feel of the
    menu, you may want to subclass this and override the template
    and/or :meth:`render` method.
    """

    template_name = "cradmin_legacy/menuitem.django.html"

    def __init__(
        self,
        label,
        url,
        active=False,
        expanded=False,
        attributes={},
        open_new_window=False,
        extra_css_classes="",
        extra_context_data=None,
    ):
        """
        Parameters:
            label: A label shown in the menu.
            url: The url to go to whem the user clicks the menu item.
            active: Should be ``True`` if the menuitem should be styled as active.
            expanded: Should be ``True`` if the menuitem should be styled as expanded.
            open_new_window: Set this to ``True`` to set the ``target="_blank"``
                attribute on the menu link.
            extra_css_classes: String with extra css classes to set on the ``<li>`` element.
        """
        self.label = label
        self.url = url
        self.attributes = attributes
        self.active = active
        self.expanded = expanded
        self.open_new_window = open_new_window
        self.extra_css_classes = extra_css_classes
        self.extra_context_data = extra_context_data
        self.childitems = []

    def get_item_css_class(self):
        return "cradmin-legacy-menu-item"

    def get_link_css_class(self):
        return ""

    def get_context_data(self):
        """
        Context data for the template.

        If you override this, make sure you call super() to get the defaults.
        """
        context_data = {"menuitem": self}
        if self.extra_context_data:
            context_data.update(self.extra_context_data)
        return context_data

    def render(self):
        return render_to_string(self.template_name, self.get_context_data())

    def get_active_item_wrapper_tag(self):
        """
        Get the wrapper tag for the active item.

        This defaults to ``None``, which means that we do not
        wrap the active item in any tag.

        You would typically override this if you hide or do not include
        the page header, and want the active menu item to be H1::

            class MyMenuItem(crmenu.Item):
                def get_active_item_wrapper_tag(self):
                    return "h1"
        """
        return None

    def is_active(self):
        """
        Returns ``True`` if the item is currently active (if ``active=True`` was
        sent to __init__).
        """
        return self.active

    def is_expanded(self):
        """
        Returns ``True`` if the item is currently expanded (if ``expanded=True`` was
        sent to __init__), or if the item :meth:`.is_active` and :meth:`.has_childitems`.
        """
        return self.expanded or (self.is_active() and self.has_childitems())

    def has_childitems(self):
        """
        Returns ``True`` if this item has child items.
        """
        return bool(self.childitems)

    def get_childitem_class(self):
        return self.__class__

    def add_childitem(self, *args, **kwargs):
        """
        Add a child of this menuitem.

        The default template will only render child items when this item
        :meth:`is_active`.
        """
        childitem_class = self.get_childitem_class()
        childitem = childitem_class(*args, **kwargs)
        self.childitems.append(childitem)
        return childitem

    def get_title(self):
        return ""


class Menu:
    """
    Base class for the menu.

    You subclass this for your site, and set
    :obj:`cradmin_legacy.crinstance.BaseInstance.menuclass`.

    In advanced cases, you may create multiple subclasses of
    this for your site, and override
    :obj:`cradmin_legacy.crinstance.BaseInstance.get_menuclass`

    Attributes:
        cradmin_instance (BaseInstance): The current cradmin instance.
        request (HttpRequest): Shortcut for ``cradmin_instance.request``.
        menu (list): A list of MenuItem objects. You use :meth:`.add`
            to add items to the menu.
    """

    #: The name of the template to use for rendering the menu.
    #: Used by :meth:`.get_template_name`.
    template_name = "cradmin_legacy/menu.django.html"

    def __init__(self, cradmin_instance):
        """
        Parameters:
            cradmin_instance (cradmin_legacy.crinstance.BaseInstance):
        """
        self.cradmin_instance = cradmin_instance
        self.request = cradmin_instance.request
        self.headeritems = []
        self.mainitems = []
        self.footeritems = []
        self.build_menu()

    def add_menuitem(self, *args, **kwargs):
        """
        Add menu item.

        args and kwargs are forwarded to the menu class (see :meth:`.get_menuitem_class`).
        """
        menuitemclass = self.get_menuitem_class()
        menuitem = menuitemclass(*args, **kwargs)
        return self.add_menuitem_object(menuitem)

    def add(self, *args, **kwargs):
        """
        Deprecated alias for :meth:`.add_menuitem`.
        """
        warnings.warn("add() is deprecated, use add_menuitem() instead.", DeprecationWarning)
        return self.add_menuitem(*args, **kwargs)

    def add_menuitem_object(self, menuitem):
        """
        Just like :meth:`.add_footeritem`, but takes a :class:`.MenuItem` instad
        of arguments for the class.
        """
        self.mainitems.append(menuitem)
        return menuitem

    def get_menuitem_class(self):
        """
        Get the class used to render each menu item.

        Returns:
            :class:`.MenuItem` by default.
        """
        return MenuItem

    def add_headeritem(self, *args, **kwargs):
        """
        Add item to the menu header.

        args and kwargs are forwarded to the menu class (see :meth:`.get_headeritem_class`).
        """
        headeritem_class = self.get_headeritem_class()
        menuitem = headeritem_class(*args, **kwargs)
        return self.add_headeritem_object(menuitem)

    def add_headeritem_object(self, menuitem):
        """
        Just like :meth:`.add_headeritem`, but takes a :class:`.MenuItem` instad
        of arguments for the class.
        """
        self.headeritems.append(menuitem)
        return menuitem

    def get_headeritem_class(self):
        """
        Get the class used to render each item in the menu header.

        Returns:
            :class:`.MenuItem` by default.
        """
        return MenuItem

    def add_footeritem(self, *args, **kwargs):
        """
        Add item to the menu footer.

        args and kwargs are forwarded to the menu class (see :meth:`.get_footeritem_class`).
        """
        footeritem_class = self.get_footeritem_class()
        return self.add_footeritem_object(footeritem_class(*args, **kwargs))

    def add_footeritem_object(self, menuitem):
        """
        Just like :meth:`.add_footeritem`, but takes a :class:`.MenuItem` instad
        of arguments for the class.
        """
        self.footeritems.append(menuitem)
        return menuitem

    def get_footeritem_class(self):
        """
        Get the class used to render each item in the menu footer.

        Returns:
            :class:`.MenuItem` by default.
        """
        return MenuItem

    def build_menu(self):
        """
        Build the menu. You HAVE to override this.

        Example::

            def build_menu(self):
                self.add(label='Home', url='/myadmin/')
                self.add(label='My menu item', url='/myadmin/my/item')
        """
        raise NotImplementedError()

    def __iter__(self):
        """
        Iterate over all items in the menu.

        Returns:
            An iterator over subclasses of :class:`.MenuItem`.
        """
        return iter(self.menu)

    def appindex_url(self, appname):
        """
        Shortcut for ``self.cradmin_instance.appindex_url(...)``.

        See :meth:`cradmin_legacy.BaseInstance.appindex_url`.
        """
        return self.cradmin_instance.appindex_url(appname)

    def roleselectview_url(self):
        """
        Shortcut for ``self.cradmin_instance.roleselectview_url()``.

        See :meth:`cradmin_legacy.BaseInstance.roleselectview_url`.
        """
        return self.cradmin_instance.roleselectview_url()

    def get_template_name(self):
        """
        Get the name of the template to use for rendering the menu.

        Defaults to :obj:`.template_name`.
        """
        return self.template_name

    def render(self, context):
        """
        Render the menu.

        Returns:
            The menu as HTML.
        """
        return render_to_string(self.get_template_name(), context)
