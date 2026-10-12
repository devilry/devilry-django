from cradmin_legacy.viewhelpers import listfilter


class ViewMixin:
    """
    Mixin class for views using filterlist.

    See :class:`cradmin_legacy.viewhelpers.listbuilderview.FilterListMixin`
    and :class:`cradmin_legacy.viewhelpers.objecttable.FilterListMixin`
    for implementation examples.
    """

    #: The :class:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`
    #: subclass to use.
    #: Defaults to :class:`cradmin_legacy.viewhelpers.listfilter.lists.Vertical`.
    filterlist_class = listfilter.lists.Vertical

    def get_filterlist_url(self, filters_string):
        """
        Get the URL for the given ``filters_string``.

        This will typically involve reversing the current view
        URL and insert ``filters_string`` as the ``filters_string``
        kwarg.
        """
        raise NotImplementedError()

    def get_filter_unprotected_querystring_arguments(self):
        """
        Get a set of names querystring arguments/attributes
        that should be not be kep when a filter is applied.

        Lets say you store the current page as ``?page=2``.
        Then you would want to return ``{'p'}`` here make sure
        applying a filter returns the user to the first page.
        """
        return set()

    def filterlist_urlbuilder(self, filters_string):
        """
        Get an urlbuilder for :class:`cradmin_legacy.viewhelpers.listfilter.base.AbstractFilterList`.

        You should not override this. Override :meth:`.get_filterlist_url` instead.
        If you override this, you have to ensure you handle querystring correctly.
        """
        querydict = self.request.GET.copy()
        unprotected_querystring_arguments = self.get_filter_unprotected_querystring_arguments()
        if unprotected_querystring_arguments:
            for unprotected_querystring_argument in unprotected_querystring_arguments:
                if unprotected_querystring_argument in querydict:
                    del querydict[unprotected_querystring_argument]

        url = self.get_filterlist_url(filters_string)
        querystring = querydict.urlencode()
        if querystring:
            url = f"{url}?{querystring}"
        return url

    def get_filters_string(self):
        """
        Get the ``filters_string`` for
        :meth:`~cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList.set_filters_string`.

        Defaults to ``kwargs.get('filters_string', '')``, which means that this just
        works as long as you use an URL pattern that looks something like this::

            r'^filter/(?P<filters_string>.+)?$'
        """
        return self.kwargs.get("filters_string", "")

    def get_filterlist_target_dom_id(self):
        """
        Get the DOM ID of the target element changed when the filters are changed.

        This element is dynamically updated by making a http request
        via javascript, looking up the target element
        (the element with the ID returned by this method) in the requested page,
        and replacing the current contents of the target element with the
        contents in the element returned dynamically.

        This means that the target element should be a wrapper around:

        - The content beeing filtered.
        - Anything that changes along with the filtered content (such as the pager)
          and any "no items message", "invalid input message" etc.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    def get_filterlist_class(self):
        """
        Get the filterlist class.

        Should return a subclass of
        :class:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`.

        Defaults to :obj:`.ViewMixin.filterlist_class`.
        """
        return self.filterlist_class

    def get_label_is_screenreader_only_by_default(self):
        """
        Defines the default value of
        :meth:`.cradmin_legacy.viewhelpers.listfilter.base.abstractfilter.AbstractFilter.get_label_is_screenreader_only`
        for all filters in the filterlist.

        This is mostly useful if you want to not show labels in your filterlist.

        Defaults to ``False``.
        """
        return False

    def get_filterlist_kwargs(self):
        """
        Get kwargs for the :meth:`.get_filterlist_class`.

        Uses:

        - :meth:`.filterlist_urlbuilder` as the ``urlbuilder``-argument for the filterlist.
        - :meth:`.get_filterlist_target_dom_id` as the ``target_dom_id``-argument for the filterlist.
        - :meth:`.get_label_is_screenreader_only_by_default` as the
          ``label_is_screenreader_only_by_default`` argument for the filterlist.

        You should not need to override this unless you create
        a filterlist with extra parameters, since we have methods
        for overriding all the parameters for
        :class:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`.
        Override the methods listed above instead.

        Note that :meth:`.filterlist_urlbuilder` should
        not be overridden directly, but you should instead override
        :meth:`.get_filterlist_url` as documented in :meth:`.filterlist_urlbuilder`.
        """
        return {
            "urlbuilder": self.filterlist_urlbuilder,
            "target_dom_id": self.get_filterlist_target_dom_id(),
            "label_is_screenreader_only_by_default": self.get_label_is_screenreader_only_by_default(),
        }

    def make_empty_filterlist(self):
        """
        Creates an empty filterlist.

        Uses:

        - :meth:`.get_filterlist_class` as the filterlist class.
        - :meth:`.get_filterlist_kwargs` as parameters when inializing the filterlist.

        You should not override this method, but instead override the
        methods above.
        """
        filterlist_class = self.get_filterlist_class()
        return filterlist_class(**self.get_filterlist_kwargs())

    def add_filterlist_items(self, filterlist):
        """
        Add items to the given ``filterlist``.

        The ``filterlist`` is created by :meth:`.make_empty_filterlist`
        by :meth:`.build_filterlist`.

        Parameters:
            filterlist: An object of a subclass of
                :class:`cradmin_legacy.viewhelpers.listfilter.base.AbstractFilterList`.
        """
        pass

    def build_filterlist(self):
        """
        Build the filterlist.

        Creates an empty filterlist with :meth:`.make_empty_filterlist`,
        then adds filters and other items with :meth:`.add_filterlist_items`,
        and sets the filters string using :meth:`.get_filters_string`.
        """
        filterlist = self.make_empty_filterlist()
        self.add_filterlist_items(filterlist=filterlist)
        filterlist.set_filters_string(filters_string=self.get_filters_string())
        return filterlist

    def get_filterlist(self):
        """
        Returns the result of :meth:`.build_filterlist`, but
        ensures the method is only called once for a request.

        This means that you should override :meth:`.build_filterlist`,
        but when you need to use it, you should call this method instead.
        """
        if not hasattr(self, "_filterlist"):
            self._filterlist = self.build_filterlist()
        return self._filterlist

    def get_filterlist_position(self):
        """
        Get the position where you want to place the filterlist.

        The supported values are defined in the mixins implemented
        in the various modules that support filterlist
        (such as :class:`cradmin_legacy.viewhelpers.listbuilderview.FilterListMixin`).
        """
        raise NotImplementedError()

    def get_filterlist_template_name(self):
        """
        Get the template to use based on what :meth:`.get_filterlist_position`.

        You will want to call this from the ``get_template_names`` method.
        This is just the interface, refer to the mixins implemented in
        various modules (such as :class:`cradmin_legacy.viewhelpers.listbuilderview.FilterListMixin`)
        for details on how to use this method.
        """
        raise NotImplementedError()

    def get_template_names(self):
        """
        You should not override this - override :meth:`.get_filterlist_template_name`
        instead.
        """
        return [self.get_filterlist_template_name()]

    def add_filterlist_to_context_data(self, context_data):
        """
        Add the context data required to render the filterlist.
        You may need to use this if you have some strange inheritance
        where get_context_data() is not called for all superclasses
        of your view.
        """
        context_data["filterlist"] = self.get_filterlist()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterlist"] = self.get_filterlist()
        return context

    def get_unfiltered_queryset_for_role(self, role):
        """
        Get a queryset with all objects of :obj:`~.ViewMixin.model`  that
        the current role can access.
        """
        raise NotImplementedError()

    def get_queryset_for_role(self, role):
        """
        Uses :meth:`.get_unfiltered_queryset_for_role` ot get the base
        queryset, then we apply the filters using
        ``get_filterlist.filter(queryset)``.

        You should not need to override this - override :meth:`.get_unfiltered_queryset_for_role`
        instead.
        """
        queryset = self.get_unfiltered_queryset_for_role(role)
        queryset = self.get_filterlist().filter(queryset)
        return queryset.distinct()
