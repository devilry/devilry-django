import logging
import urllib
from collections import OrderedDict

from cradmin_legacy.viewhelpers.listfilter.base.exceptions import (
    InvalidFiltersStringError,
)

logger = logging.getLogger(__name__)


class FiltersHandler:
    """
    Parser of the ``filters_string``. See :meth:`.AbstractFilterList.parse_filters_string`.
    """

    #: The string separating filters in the filters string. Defaults to ``"/=/"``.
    filter_separator = "$-/-$"

    #: The string used to separate filter slug and value.
    #: It does not matter if this also appears in the value,
    #: we handle that by splitting with a maxsplit of 1.
    #:
    #: Defaults to ``"-"``.
    slug_and_value_separator = "-"

    #: The string used to separate multivalue strings.
    #: This string can not appear in any value used by the filter.
    #:
    #: Defaults to ``","``.
    multivalue_separator = ","

    def __init__(self, urlbuilder):
        """
        Parameters:
            urlbuilder: A method that takes a single argument, ``filters_string``,
                and returns an absolute URL with that string injected as the
                filters string. The filters_string is urlencoded, so you should
                be able to just forward it to ``reverse`` for your view.
        """
        self.filtermap = OrderedDict()
        self.urlbuilder = urlbuilder
        self._parse_called = False

    def split_raw_filter_values(self, raw_values):
        """
        Parse the given ``value``, splitting it into a list of values.

        You can override this if just overriding :obj:`.FiltersHandler.multivalue_separator`
        is not powerful enough.

        If you override this, you will also have ot override :meth:`.join_filter_values`.
        """
        values = urllib.parse.unquote_plus(raw_values)
        return [urllib.parse.unquote_plus(value) for value in values.split(self.multivalue_separator)]

    def join_filter_values(self, values):
        """
        The reverse of :meth:`.split_raw_filter_values`. Joins
        the given ``values`` list into a string.
        """
        # We quote each value, and then we quote the entire string. This
        # ensures that we do not get any problems when a value contains
        # ``multivalue_separator``.
        raw_values = [urllib.parse.quote_plus(value) for value in values]
        raw_values = self.multivalue_separator.join(raw_values)
        return urllib.parse.quote_plus(raw_values)

    def parse_filter_string(self, filter_string):
        """
        Parse the given ``filter_string`` and return a ``(slug, values)`` tuple,
        where ``slug`` is a filter slug and ``values`` is a list of strings.

        You should not need to override this.
        """
        if self.slug_and_value_separator not in filter_string:
            raise InvalidFiltersStringError(f'"{filter_string}" does not contain "{self.slug_and_value_separator}".')
        slug, value = filter_string.split(self.slug_and_value_separator, 1)
        return slug, self.split_raw_filter_values(value)

    def parse(self, filters_string):
        """
        Parse the given ``filters_string`` and add any values
        found in the string to the corresponding filter.

        You should not need to override this.
        """
        if self._parse_called:
            raise RuntimeError("Can not call parse multiple times on a FiltersHandler.")
        self._parse_called = True

        if not filters_string:
            return

        if filters_string.startswith(self.filter_separator):
            filters_string = filters_string[len(self.filter_separator) :]
        if filters_string.endswith(self.filter_separator):
            filters_string = filters_string[: -len(self.filter_separator)]
        for filter_string in filters_string.split(self.filter_separator):
            slug, values = self.parse_filter_string(filter_string)
            if slug in self.filtermap:
                self.filtermap[slug].set_values(values)
            else:
                logger.debug(f'"{slug}" is not a valid filter slug.')

    def add_filter(self, filterobject):
        """
        Add a :class:`.AbstractFilter` to the handler.
        """
        slug = filterobject.get_slug()
        if slug in self.filtermap:
            raise ValueError(f'Duplicate slug: "{slug}".')
        if self.slug_and_value_separator in slug:
            raise ValueError(f'Invalid filter slug: "{slug}". Slugs can not contain "{self.slug_and_value_separator}".')
        self.filtermap[slug] = filterobject

    def normalize_values(self, values):
        """
        Normalize values list to only contain
        ``bool(value) == True`` values. Since values
        is a list of strings, this means that it strips
        out all empty strings.
        """
        return [value for value in values if value]

    def build_filter_string(self, slug, values):
        """
        Build a filter string suitable for an URL from the given
        ``slug`` and ``values``.

        Parameters:
            slug: See :meth:`.AbstractFilter.get_slug`.
            value: A list of values. All items in the list must be strings.
        """
        return "{slug}{separator}{values}".format(
            slug=slug, separator=self.slug_and_value_separator, values=self.join_filter_values(values=values)
        )

    def build_filters_string(self, changed_filterobject):
        """
        Build the ``filters_string`` for :meth:`.build_filter_url`.
        """
        filters_strings = []
        for slug, filterobject in self.filtermap.items():
            if filterobject.get_slug() == changed_filterobject.get_slug():
                values = changed_filterobject.values
            else:
                values = filterobject.values
            values = self.normalize_values(values)
            if values:
                filters_strings.append(self.build_filter_string(slug=slug, values=values))
        return self.filter_separator.join(filters_strings)

    def build_filter_url(self, changed_filterobject):
        """
        Build an URL that applies the change introduced by
        ``changed_filterobject`` while keeping any values
        in all the other filters within the handler.

        Parameters:
            changed_filterobject: A :class:`.AbstractFilter` object.
        """
        filters_string = self.build_filters_string(changed_filterobject=changed_filterobject)
        return self.urlbuilder(filters_string=filters_string)

    def filter(self, queryobject, exclude=None):
        """
        Apply the filters to the given ``queryobject``.

        Loops through all the registered filters (the filters added with :meth:`.add_filter`),
        and run :meth:`.AbstractFilter.filter`.

        Parameters:
            queryobject: See :meth:`.AbstractFilter.filter`.
            exclude: Set with the slugs of filters to ignore/exclude when filtering.
                Defaults to ``None``, which means that all filters are applied.
        """
        for filterobject in self.filtermap.values():
            if exclude and filterobject.get_slug() in exclude:
                continue
            queryobject = filterobject.filter(queryobject=queryobject)
        return queryobject

    def get_label_for(self, slug):
        """
        Get the label for the filter registered in the filterhandler with the given ``slug``.

        Raises:
            KeyError: If the ``slug`` is not registered.
        """
        return self.filtermap[slug].get_label()

    def get_cleaned_value_for(self, slug):
        """
        Get the cleaned value for the filter registered in the filterhandler
        with the given ``slug``.

        Raises:
            KeyError: If the ``slug`` is not registered.
        """
        return self.filtermap[slug].get_cleaned_value()

    def get_cleaned_values_for(self, slug):
        """
        Get the cleaned values (list) for the filter registered in the filterhandler
        with the given ``slug``.

        Raises:
            KeyError: If the ``slug`` is not registered.
        """
        return self.filtermap[slug].get_cleaned_values()
