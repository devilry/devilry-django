import json
from xml.sax.saxutils import quoteattr
from django.utils.translation import pgettext
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlistchild import AbstractFilterListChild


class AbstractFilter(AbstractFilterListChild):
    """
    Abstract base class for all filters.
    """

    template_name = "cradmin_legacy/viewhelpers/listfilter/base/abstractfilter.django.html"

    def __init__(self, slug=None, label=None, label_is_screenreader_only=None):
        """
        Parameters:
            slug: You can send the slug as a parameter, or override :meth:`.get_slug`.
            label: You can send the label as a parameter, or override :meth:`.get_label`.
            label_is_screenreader_only: You can set this as a parameter,
                or override :meth:`.get_label_is_screenreader_only`.
        """
        self.values = []
        self.slug = slug
        self.label = label
        self.label_is_screenreader_only = label_is_screenreader_only
        super().__init__()

    def copy(self):
        """
        Returns a copy of this filter.
        """
        copy = self.__class__()
        copy.set_values(list(self.values))
        copy.slug = self.slug
        copy.label = self.label
        return copy

    def get_slug(self):
        """
        Get the slug for this filter. The slug is used
        in the URL to identify the filter.

        If your users can change their language, this
        should not be translatable since that would
        make an URL unusable by a user with a different language
        (if a user shares an URL with another user).
        """
        if self.slug:
            return self.slug
        else:
            raise NotImplementedError("You must override get_slug(), or send a slug to __init__().")

    def get_label(self):
        """
        Get the label of the filter. This is typically set as the
        ``<label>`` for the filter input field.

        A label is optional, but highly recommended. Even if you do not
        want to show the label, you should specify one, and hide it
        from everyone except for screenreaders with
        :meth:`.get_label_is_screenreader_only`.
        """
        return self.label

    def get_label_is_screenreader_only(self):
        """
        If this returns ``True``, the label will be styled to
        only make it visible to screenreaders.

        This is recommended over simply not setting a label
        since that would break accessibility.

        Defaults to the value of the ``label_is_screenreader_only`` parameter
        (see :class:`.AbstractFilter`). If ``label_is_screenreader_only`` is ``None``,
        this defaults to the return value of the ``get_label_is_screenreader_only_by_default()``
        method of
        :class:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`.
        """
        if self.label_is_screenreader_only is None:
            return self.filterlist.get_label_is_screenreader_only_by_default()
        else:
            return self.label_is_screenreader_only

    def set_values(self, values):
        """
        Change the current values stored in the filter to the given ``values``.
        """
        self.values = values

    def clear_values(self):
        """
        Clear the current values stored in the filter.
        """
        self.values = []

    def add_values(self, values):
        """
        Add the given list of ``values`` to the values currently stored
        in the filter.
        """
        self.values += values

    def remove_values(self, values):
        """
        Remove the given list of ``values`` from the values currently stored
        in the filter.
        """
        new_values = list(self.values)
        values_to_remove = values
        for value in new_values:
            if value in values_to_remove:
                new_values.remove(value)
        self.values = new_values

    def clean_value(self, value):
        """
        Called by :meth:`.clean_values` to clean a single value.
        """
        return value

    def get_cleaned_values(self):
        """
        Clean the values, to prepare them for usage in :meth:`.filter`.

        Defaults to returning the values unchanged, but you will typically
        want to override this if your filter allows the user to type in a
        values, or if you want to convert the values from a string into
        something that makes sense for your :meth:`.filter`.

        If you want validation, you should handle that by setting some
        attribute on ``self``, and handle the error in the template
        rendering the filter (and most likely not add anything
        to the queryobject in :meth:`.filter`).
        """
        return [self.clean_value(value) for value in self.values]

    def get_cleaned_value(self):
        """
        Returns the first value returned by :meth:`.get_cleaned_values`,
        or ``None`` if there is no values. Use this in
        :meth:`.filter` if you expect a single value.
        """
        clean_values = self.get_cleaned_values()
        if len(clean_values) > 0:
            return clean_values[0]
        else:
            return None

    def build_set_values_url(self, values):
        """
        Get the URL that adds this filter with the given values to the current url.

        You should not need to override this, but you will use it in your
        template context to render urls for choices if your filter
        is a single select filter.
        """
        copy = self.copy()
        copy.set_values(values)
        return self.filterlist.filtershandler.build_filter_url(changed_filterobject=copy)

    def build_clear_values_url(self):
        """
        Get the URL that clears this filter from the current url.

        You should not need to override this, but you will use it in your
        template context to render urls for choices if your filter
        supports "clear".
        """
        copy = self.copy()
        copy.clear_values()
        return self.filterlist.filtershandler.build_filter_url(changed_filterobject=copy)

    def build_add_values_url(self, values):
        """
        Get the URL that adds the given values for this filter to the current url.

        This is not the same as :meth:`.build_set_values_url`. This method is for
        multiselect filters where the user can add valuess to the filter
        (typically via checkboxes).

        You should not need to override this, but you will use it in your
        template context to render urls for choices if your filter
        uses multiselect.
        """
        copy = self.copy()
        copy.add_values(values)
        return self.filterlist.filtershandler.build_filter_url(changed_filterobject=copy)

    def build_remove_values_url(self, values):
        """
        Get the URL that removes the given values for this filter to the current url.

        This is not the same as :meth:`.build_clear_values_url`. This method is for
        multiselect filters where the user can add/remove valuess to the filter
        (typically via checkboxes).

        You should not need to override this, but you will use it in your
        template context to render urls for choices if your filter
        uses multiselect.
        """
        copy = self.copy()
        copy.remove_values(values)
        return self.filterlist.filtershandler.build_filter_url(changed_filterobject=copy)

    def get_base_css_classes_list(self):
        return ["cradmin-legacy-listfilter-filter"]

    def filter(self, queryobject):
        """
        Add the current values to the given ``queryobject``.

        This is always called unless the ``filter_string`` is
        None or empty string.

        Parameters:
            queryobject: The type of the queryobject depends on the query backend.
                If you are filtering against the Django ORM, this will
                typically be a QuerySet, but for other backends such
                as ElasticSearch, MongoDB, etc. this can be something
                completely different such as a dict.

        Returns:
            An object of the same type as the given ``queryobject``.
        """
        raise NotImplementedError()

    def get_dom_id(self):
        """
        Get the DOM ID of this filter. The base template adds this to the wrapping DIV,
        but you can also use this if you need DOM IDs for components of a filter
        (E.g.: Field ID to attach a labels to a form field).
        """
        return f"{self.filterlist.get_dom_id_prefix()}_{self.get_slug()}"

    def get_label_dom_id(self):
        """
        Get the DOM ID of the label for this filter.
        """
        return f"{self.get_dom_id()}_label"

    def get_inputfield_dom_id(self):
        """
        Get the DOM id of the input field. If the filter uses multiple input fields,
        this will most likely not be used, or it may be used as the ID of the
        first field to make the label focus on the first field when it is clicked.
        """
        return f"{self.get_dom_id()}_input"

    def get_target_dom_id(self):
        """
        Get the DOM id of the target of the filter.
        This is just a shortcut to access
        :meth:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList.get_target_dom_id`.
        """
        return self.filterlist.get_target_dom_id()

    def get_loadingmessage(self):
        """
        Get the loading message to show when the filter loads
        the updated target element content.
        """
        return pgettext("listfilter loading message", "Loading")

    def get_angularjs_options_dict(self):
        """
        Get angularjs directive options dict.

        You can override this in your filters, but you should
        call ``super`` to get the default options.
        """
        return {"loadingmessage": self.get_loadingmessage()}

    def get_angularjs_options_json(self):
        """
        Returns a json encoded and HTML attribute quoted version
        of :meth:`.get_angularjs_options_dict`.

        You use this with the angularjs directive for the filter
        to send options into the directive::

            <someelement my-filter-directive={{ me.get_angularjs_options_json|safe }}>

        Notice that we do not include any ``"`` or ``'`` around the directives
        HTML attribute - that is included by this method.
        """
        return quoteattr(json.dumps(self.get_angularjs_options_dict()))
