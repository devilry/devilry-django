class QuerysetForRoleMixin(object):
    """
    Common mixin class for views that query for items limited to
    items accessible by the current cradmin role.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.mixins.QuerysetForRoleMixin``.
    """

    def get_queryset_for_role(self):
        """
        Get a queryset with all objects of ``self.model``  that
        the current role can access.
        """
        raise NotImplementedError()

    def get_queryset(self):
        """
        DO NOT override this. Override :meth:`.get_queryset_for_role`
        instead.
        """
        queryset = self.get_queryset_for_role()
        return queryset


class CommonCradminViewMixin(object):
    """
    Common mixin class for all cradmin view classes.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.mixins.CommonCradminViewMixin``.
    """

    def add_breadcrumb_list_items(self, breadcrumb_item_list):
        """
        Add items to the breadcrumb item list.

        If you completely override the :meth:`.get_breadcrumb_item_list_renderable` method
        without calling super (or calling this method explicitly), this method will have no effect.

        Examples:

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
        Get a breadcrumb item list renderable to use when rendering the template for this view.

        By default, this just uses ``request.cradmin_app.get_breadcrumb_item_list_renderable()``
        (see :meth:`django_cradmin.crapp.App.get_breadcrumb_item_list_renderable`).

        You will normally only want to override this if you want to customize how breadcrumbs
        are rendered. If you just need to add items to the breadcrumb item list, override
        :meth:`.add_breadcrumb_list_items`.

        If you override this, remember that the breadcrumb item list from
        ``request.cradmin_app.get_breadcrumb_item_list_renderable()``
        can be ``None``, so if you use that method you have to remember to handle this.

        Returns:
            django_cradmin.crbreadcrumb.BreadcrumbItemList: A breadcrumb item list renderable object
                or ``None``.

        .. seealso:: :doc:`/crbreadcrumb`
        """
        if hasattr(self.request, "cradmin_app"):
            breadcrumb_item_list = self.request.cradmin_app.get_breadcrumb_item_list_renderable()
            if breadcrumb_item_list is not None:
                self.add_breadcrumb_list_items(breadcrumb_item_list=breadcrumb_item_list)
                return breadcrumb_item_list
        return None

    def add_common_view_mixin_data_to_context(self, context):
        """
        Call this to add common template context variables to the provided ``context``.

        Do not override this in subclasses, but if you create a class that uses this
        mixin, you **must** call this in your ``get_context_data()``-method.

        Args:
            context (dict): A template context.
        """
        context["cradmin_breadcrumb_item_list"] = self.get_breadcrumb_item_list_renderable()
