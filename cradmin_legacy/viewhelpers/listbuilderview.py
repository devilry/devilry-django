from django.conf import settings
from django.template import defaultfilters
from django.views.generic import ListView
from cradmin_legacy.viewhelpers import listbuilder
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers.listfilter import listfilter_viewmixin
from cradmin_legacy.viewhelpers import listfilter


class ViewMixin:
    """
    Listbuilder view mixin. Must be mixin in before any Django View subclass.

    This is typically used with a Django ListView or TemplateView.
    The mixin is not dependent on any specific backend, so it works
    no matter where you get your data from (database, mongodb, elasticsearch, ...).

    For a ready to use view that extends this to work with Django model objects,
    see :class:`.View`.

    The ViewMixin works much like :class:`.View`, but you must override/implement:

    - :meth:`.get_pagetitle`
    - :meth:`.get_listbuilder_list_value_iterable`
    - :meth:`.get_no_items_message`
    """

    template_name = "cradmin_legacy/viewhelpers/listbuilderview/default.django.html"

    #: See :meth:`~ViewMixin.get_listbuilder_class`.
    listbuilder_class = listbuilder.lists.RowList

    #: See :meth:`~ViewMixin.get_value_renderer_class`.
    value_renderer_class = listbuilder.itemvalue.FocusBox

    #: See :meth:`~ViewMixin.get_frame_renderer_class`.
    frame_renderer_class = listbuilder.itemframe.DefaultSpacingItemFrame

    #: Set this to True to hide the page header. See :meth:`~.FormViewMixin.get_hide_page_header`.
    hide_page_header = False

    #: Enable previews? See :meth:`.get_enable_previews`. Defaults to ``False``.
    enable_previews = False

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def get_pageheading(self):
        """
        Get the page heading.

        Defaults to :meth:`.get_pagetitle`.
        """
        return self.get_pagetitle()

    def get_hide_page_header(self):
        """
        Return ``True`` if we should hide the page header.

        You can override this, or set :obj:`.hide_page_header`, or hide the page header
        in all form views with the ``CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_LISTVIEWS`` setting.
        """
        return self.hide_page_header or getattr(settings, "CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_LISTVIEWS", False)

    def get_enable_previews(self):
        """
        If this returns ``True``, we enable previews.

        This is required for the ``cradmin-legacy-page-preview-open-on-click``
        angularJS directive to work.

        Defaults to :obj:`.enable_previews`.
        """
        return self.enable_previews

    def get_listbuilder_class(self):
        """
        Get a subclass of :class:`cradmin_legacy.viewhelpers.listbuilder.base.List`.

        Defaults to :obj:`.ViewMixin.listbuilder_class`.
        """
        return self.listbuilder_class

    def get_listbuilder_list_kwargs(self):
        """
        Get kwargs for :meth:`.get_listbuilder_class`.
        """
        return {}

    def get_value_and_frame_renderer_kwargs(self):
        """
        Get kwargs for the classes returned by :meth:`.get_value_renderer_class`
        and :meth:`.get_frame_renderer_class`.

        Both the frame and value renderer base classes takes ``**kwargs``
        and store them in ``self.kwargs`` (just like django class based views),
        so even if you just need to send kwargs to one of these classes,
        you can still use this.

        See the docs for the ``value_and_frame_renderer_kwargs`` argument for
        :meth:`cradmin_legacy.viewhelpers.listbuilder.base.List.extend_with_values`
        method for more information. HINT: This can also return a callable to generate
        kwargs based on each value in the list!
        """
        return {}

    def get_value_renderer_class(self):
        """
        Get a subclass of :class:`cradmin_legacy.viewhelpers.listbuilder.base.ItemValueRenderer`.

        Defaults to :obj:`.ViewMixin.value_renderer_class`.
        """
        return self.value_renderer_class

    def get_frame_renderer_class(self):
        """
        Get a subclass of :class:`cradmin_legacy.viewhelpers.listbuilder.base.ItemFrameRenderer`.

        Defaults to :obj:`.ViewMixin.frame_renderer_class`.
        """
        return self.frame_renderer_class

    def get_listbuilder_list_value_iterable(self, context):
        """
        Get the value_iterable for the listbuilder list.

        Must be overridden in subclasses.

        Parameters:
            context: The Django template context.
        """
        raise NotImplementedError()

    def get_listbuilder_list(self, context):
        """
        Get the listbuilder List object.

        You normally do not have to override this, but instead you should
        override:

        - :meth:`.get_listbuilder_list_value_iterable`
        - :meth:`.get_value_renderer_class`
        - :meth:`.get_frame_renderer_class`
        - :meth:`.get_value_and_frame_renderer_kwargs`
        - :meth:`.get_listbuilder_list_kwargs`

        Parameters:
            context: The Django template context.
        """
        return self.get_listbuilder_class().from_value_iterable(
            value_iterable=self.get_listbuilder_list_value_iterable(context),
            value_renderer_class=self.get_value_renderer_class(),
            frame_renderer_class=self.get_frame_renderer_class(),
            value_and_frame_renderer_kwargs=self.get_value_and_frame_renderer_kwargs(),
            **self.get_listbuilder_list_kwargs(),
        )

    def get_no_items_message(self):
        """
        Get the message to show when there are no items.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    def add_listview_context_data(self, context):
        context["listbuilder_list"] = self.get_listbuilder_list(context)
        context["pagetitle"] = self.get_pagetitle()
        context["hide_pageheader"] = self.get_hide_page_header()
        context["pageheading"] = self.get_pageheading()
        context["no_items_message"] = self.get_no_items_message()
        context["enable_previews"] = self.get_enable_previews()
        context["pre_include_template"] = self.get_pre_include_template()
        context["buttons_include_template"] = self.get_buttons_include_template()
        context["post_include_template"] = self.get_post_include_template()

    def get_pre_include_template(self):
        """
        You can return a template to include before the listbuilder list here.
        """
        return None

    def get_buttons_include_template(self):
        """
        You can return a template to include buttons above the
        listbuilder list here. If you include this template,
        we will create a ``<p>`` with ``cradmin-legacy-listbuilderview-buttons``
        as css class, and include your template within that ``<p>``.
        """
        return None

    def get_post_include_template(self):
        """
        You can return a template to include after the listbuilder list here.
        """
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_listview_context_data(context)
        return context


class ViewCreateButtonMixin:
    """
    Mixin class that overrides :meth:`.View.get_buttons_include_template`
    with a template that renders a create button that assumes the
    create view is named ``"create"``.
    """

    def get_buttons_include_template(self):
        return "cradmin_legacy/viewhelpers/listbuilderview/includes/create-button.django.html"


class View(ViewMixin, ListView):
    """
    View using the :doc:`viewhelpers_listbuilder`.

    Examples:

        Minimal::

            from cradmin_legacy.viewhelpers import listbuilderview

            class MyView(listbuilderview.View):
                def get_queryset(self):
                    return MyModel.objects.all()

    """

    #: The model class to list objects for. You do not have to specify
    #: this, but if you do not specify this or :meth:`~.ObjectTableView.get_model_class`,
    #: you have to override :meth:`~.ObjectTableView.get_pagetitle` and
    #: :meth:`~.ObjectTableView.get_no_items_message`.
    model = None

    #: Set this to ``True`` to make the template not render the menu.
    #: Very useful when creating foreign-key select views, and other views
    #: where you do not want your users to accidentally click out of the
    #: current view.
    hide_menu = False

    def get_model_class(self):
        """
        Get the model class to list objects for.

        Defaults to :obj:`~.View.model`. See :obj:`~.View.model` for more info.
        """
        return self.model

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to the ``verbose_name_plural`` of the :obj:`~.View.model`
        with the first letter capitalized.
        """
        return defaultfilters.capfirst(self.get_model_class()._meta.verbose_name_plural)

    def get_listbuilder_list_value_iterable(self, context):
        return context["object_list"]

    def get_queryset_for_role(self, role):
        """
        Get a queryset with all objects of :obj:`~.View.model`  that
        the current role can access.
        """
        raise NotImplementedError()

    def get_queryset(self):
        """
        DO NOT override this. Override :meth:`.get_queryset_for_role`
        instead.
        """
        queryset = self.get_queryset_for_role(self.request.cradmin_role)
        return queryset

    def get_no_items_message(self):
        """
        Get the message to show when there are no items.
        """
        return gettext_lazy("No %(modelname_plural)s") % {
            "modelname_plural": self.get_model_class()._meta.verbose_name_plural.lower(),
        }

    def disable_paging_requested(self):
        """
        If this returns ``True``, we disable paging.

        The default implementation disables paging if ``disablePaging=true`` is
        in the querystring (in ``request.GET``).

        When pagination is enabled for the listbuilder-view, disabling pagination
        will also be supported to be able to load all instead of just the next page.
        """
        return self.request.GET.get("disablePaging", "false") == "true"

    def get_paginate_by(self, queryset):
        """
        Built-in support for pagination.

        Will return the set pagination (paginate_by), or disable pagination
        if `self.disable_paging_requested` returns `True`.
        """
        if self.disable_paging_requested():
            return None
        return self.paginate_by

    def use_pagination_load_all(self):
        """
        If pagination is enabled, requesting the next page
        will load all, not only the next page.

        This is used to tell the UI that the pagination should load
        all elements, not just the next page setting the javasscript
        pagination-handling mode to "loadAllOnClick".

        If `True`, the page-load will load all elements, and the
        button will also show "Load all" intead of "Load more".
        """
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cradmin_hide_menu"] = self.hide_menu
        context["pagination_mode_load_all"] = self.use_pagination_load_all()
        return context


class FilterListMixin(listfilter_viewmixin.ViewMixin):
    """
    Mixin for adding filtering with :doc:`viewhelpers.listfilter <viewhelpers_listfilter>` to
    :class:`listbuilder View <.View>`.

    Must be mixed in before any TemplateView subclass.
    """

    template_name = None

    def get_filterlist_position(self):
        """
        Get the position where you want to place the filterlist.

        Supported values are:

        - left
        - right (the default)
        - top

        Defaults to ``"top"`` if :meth:`.get_filterlist_class` returns
        :class:`cradmin_legacy.viewhelpers.listfilter.lists.Horizontal` or a subclass of it,
        otherwise ``"right"``.
        """
        filterlist_class = self.get_filterlist_class()
        if issubclass(filterlist_class, listfilter.lists.Horizontal):
            return "top"
        else:
            return "right"

    def get_filterlist_template_name(self):
        """
        Get the template to use based on what :meth:`.get_filterlist_position`.

        You will want to call this from the ``get_template_names`` method.
        This is just the interface, refer to the mixins implemented in
        various modules (such as :class:`cradmin_legacy.viewhelpers.listbuilderview.FilterListMixin`)
        for details on how to use this method.
        """
        if getattr(self, "template_name", None):
            return self.template_name
        else:
            position = self.get_filterlist_position()
            template_name = f"cradmin_legacy/viewhelpers/listbuilderview/filterlist-{position}.django.html"
            return template_name

    def get_filter_unprotected_querystring_arguments(self):
        """
        This returns ``{'page'}``, which ensures we go back to
        page 1 when changing a filter.

        See :class:`cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin`
        for more details.
        """
        return {"page"}

    def get_filterlist_target_dom_id(self):
        """
        Overrides
        :meth:`cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin.get_filterlist_target_dom_id`
        with a default of ``"cradmin_legacy_listbuilderview_listwrapper"``.

        You should not need to override this unless you create a completely custom
        template for your view.
        """
        return "cradmin_legacy_listbuilderview_listwrapper"
