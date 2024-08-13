from cradmin_legacy.viewhelpers.listfilter.lists import Vertical
from cradmin_legacy.viewhelpers.listfilter.base.filtershandler import FiltersHandler


class DevilryVertical(Vertical):
    """
    An :class:`~cradmin_legacy.viewhelpers.listfilter.lists.vertical` with FiltersHandler that ignores
    invalid filters instead of raising InvalidListFiltersStringError.
    """

    def get_filters_handler_class(self):
        return DevilryFiltersHandler


class DevilryFiltersHandler(FiltersHandler):
    def parse(self, filters_string):
        """
        Parse the given ``filters_string`` and add any values
        found in the string to the corresponding filter.

        You should not need to override this.
        """
        if self._parse_called:
            raise RuntimeError('Can not call parse multiple times on a FiltersHandler.')
        self._parse_called = True

        if not filters_string:
            return

        filters_string = filters_string.strip(self.filter_separator)
        for filter_string in filters_string.split(self.filter_separator):
            slug, values = self.parse_filter_string(filter_string)
            if slug in self.filtermap:
                self.filtermap[slug].set_values(values)
