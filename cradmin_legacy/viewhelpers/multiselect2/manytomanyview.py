import json

from django import forms
from django.views.generic.edit import FormMixin

from cradmin_legacy.viewhelpers.multiselect2 import listbuilder_itemvalues
from cradmin_legacy.viewhelpers.multiselect2 import target_renderer


class ViewMixin(FormMixin):
    """
    Base class for the mixin classes for views that is shown in an iframe
    by :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.
    """

    hide_menu = True

    #: The default target renderer task. Should be a subclass of
    #: :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.ManyToManySelectTarget`.
    target_renderer_class = target_renderer.ManyToManySelectTarget

    form_class = forms.Form

    def get_selected_values_list(self):
        """
        Returns:
            list: json decodes ``request.GET['manytomany_select_current_value']``
            and returns the result.
        """
        return json.loads(self.request.GET["manytomany_select_current_value"])

    def get_selected_objects(self):
        """
        Make a queryset from :meth:`.get_selected_values_list`.

        Supports :class:`.cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin`
        out of the box, so if a ``get_unfiltered_queryset_for_role()``-method is available
        on the class, we use that instead of ``get_queryset_for_role()``.

        Returns:
            django.db.QuerySet: A queryset with the model objects matching
            :meth:`.get_selected_values_list`. Defaults to filtering
            the values with ``pk__in=<get_selected_values_list()>``.
        """
        if hasattr(self, "get_unfiltered_queryset_for_role"):
            queryset = self.get_unfiltered_queryset_for_role(self.request.cradmin_role)
        else:
            queryset = self.get_queryset_for_role(self.request.cradmin_role)
        return queryset.filter(pk__in=self.get_selected_values_list())

    def should_include_previously_selected(self):
        """
        This should return ``True`` if we want to include the values in
        :meth:`.get_selected_objects` in the list.

        This should be ``True`` for the initial page load, which means
        that it should be ``True`` if we are one the first page, and no
        filtering/searching is applied.

        Returns:
            bool: Should we include previously selected values in the listbuilder list.
        """
        if hasattr(self, "get_filters_string") and self.get_filters_string():
            return False
        elif getattr(self, "paginate_by", None):
            page_kwarg = self.page_kwarg
            page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
            return str(page) == "1"
        else:
            return True

    def get_queryset_for_role(self, role=None):
        queryset = super().get_queryset_for_role(role=role)
        if self.should_include_previously_selected():
            # We have to exclude the selected values because we add them
            # to the listbuilder list as selected items in :meth:`.get_listbuilder_list`.
            queryset = queryset.exclude(pk__in=self.get_selected_values_list())
        return queryset

    def get_target_renderer_class(self):
        """
        Returns:
            cradmin_legacy.viewhelpers.multiselect2.target_renderer.ManyToManySelectTarget: The target renderer
            class.
        """
        return self.target_renderer_class

    def get_target_renderer_kwargs(self):
        """
        Returns:
            dict: Keyword arguments for the constructor of :meth:`.get_target_renderer_class`.
        """
        return {
            "target_formfield_id": self.request.GET["manytomany_select_fieldid"],
            "empty_selection_allowed": self.request.GET["manytomany_select_required"] != "True",
            "form": self.get_form(form_class=self.get_form_class()),
        }

    def get_target_renderer(self):
        """
        Get a select target renderer. Defaults to returning the
        :meth:`.get_target_renderer_class` initialized with
        :meth:`.get_target_renderer_kwargs`.
        """
        targer_renderer_class = self.get_target_renderer_class()
        return targer_renderer_class(**self.get_target_renderer_kwargs())


class ListBuilderViewMixin(ViewMixin):
    """
    Mixin class for using a listbuilder view as a select view for
    :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.

    You only need to render the target renderable returned by
    :meth:`.ViewMixin.get_target_renderer`. You will typically
    do this by adding it in ``get_context_data()``, and render it with
    :meth:`cradmin_legacy.templatetags.cradmin_legacy_tags.cradmin_render_renderable`.

    Examples:

        Simple example::

            from cradmin_legacy.viewhelpers import listbuilderview
            from cradmin_legacy.viewhelpers import multiselect2

            class MySelectView(multiselect2.manytomanyview.ListBuilderViewMixin,
                               listbuilderview.FilterListMixin,
                               listbuilderview.View):
                def get_queryset_for_role(self, role):
                    ...

                def get_context_data(self, context):
                    context = super(MySelectView, self).get_context_data(context)
                    context['target_renderer'] = self.get_target_renderer()
                    return context
    """

    value_renderer_class = listbuilder_itemvalues.ManyToManySelect

    def get_listbuilder_list(self, context):
        listbuilder_list = super().get_listbuilder_list(context=context)
        if self.should_include_previously_selected():
            value_renderer_class = self.get_value_renderer_class()
            frame_renderer_class = self.get_frame_renderer_class()
            listbuilder_list.extend_with_values(
                value_iterable=self.get_selected_objects(),
                value_renderer_class=value_renderer_class,
                frame_renderer_class=frame_renderer_class,
                value_and_frame_renderer_kwargs={"is_selected": True},
            )
        return listbuilder_list


class ListBuilderFilterListViewMixin(ListBuilderViewMixin):
    """
    Mixin class for using a listbuilder view with filterlist as a select view for
    :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.

    You only need to render the target renderable returned by
    :meth:`.ViewMixin.get_target_renderer`. You will typically
    do this by adding it in ``get_context_data()``, and render it with
    :meth:`cradmin_legacy.templatetags.cradmin_legacy_tags.cradmin_render_renderable`.


    Examples:

        Simple example::

            from cradmin_legacy.viewhelpers import listbuilderview
            from cradmin_legacy.viewhelpers import multiselect2

            class MySelectView(multiselect2.manytomanyview.ListBuilderFilterListViewMixin,
                               listbuilderview.FilterListMixin,
                               listbuilderview.View):
                def get_queryset_for_role(self, role):
                    ...
    """

    def get_filterlist_url(self, filters_string):
        """
        Implements :meth:`cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin#get_filterlist_url`
        with a default that assumes you have a view named ``manytomanyselect-filter``
        that takes ``filters_string`` as kwarg.
        """
        return self.request.cradmin_app.reverse_appurl(
            "manytomanyselect-filter", kwargs={"filters_string": filters_string}
        )

    def add_target_renderer_to_filterlist(self, filterlist):
        """
        Add the :meth:`~.ListBuilderViewMixin.get_target_renderer` to the filter list.
        """
        filterlist.append(self.get_target_renderer())

    def add_filterlist_items(self, filterlist):
        """
        Automatically adds the :meth:`~.ListBuilderViewMixin.get_target_renderer`
        to the filter list.

        Uses :meth:`.add_target_renderer_to_filterlist` to add the target renderer,
        so if you want to add the target renderer some other place, you
        can just override that method in a subclass.
        """
        super().add_filterlist_items(filterlist=filterlist)
        self.add_target_renderer_to_filterlist(filterlist=filterlist)
