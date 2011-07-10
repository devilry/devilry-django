from fnmatch import fnmatchcase



class FilterValidationError(Exception):
    """ Raised when an invalid filter is given to
    :meth:`devilry.simplified.SimplifiedModelApi.search`. """

class FilterSpec(object):
    """ Specifies that a specific field can be filtered, and what filtering
    operation it can do. Filtering operations are those supported by Django,
    such as *exact* and *gte*. """
    def __init__(self, fieldname, operations=('', 'exact', 'iexact',
                                              'lt', 'gt', 'lte', 'gte',
                                              'contains', 'icontains',
                                              'startswith', 'endswith')):
        """
        :param fieldname: The field to allow filtering on.
        :param operations: The allowed operations. Note that ``''`` is the same
            as ``'exact'``.
        """
        self.fieldname = fieldname
        self.operations = operations

    def _yield(self, value):
        return False, value

    def __iter__(self):
        for operation in self.operations:
            if operation == '':
                yield self._yield(self.fieldname)
            else:
                yield self._yield('{0}__{1}'.format(self.fieldname, operation))


class PatternFilterSpec(FilterSpec):
    def _yield(self, value):
        return True, value


class ForeignFilterSpec(object):
    """ Specify FilterSpec for foreign tables without having to type
    ``__`` for each table. Instead of::

        FilterSpecs(FilterSpec('parentnode__parentnode__short_name'),
                    FilterSpec('parentnode__parentnode__longname'))

    We can do::

        FilterSpecs(ForeignFilterSpec('parentnode__parentnode',
                                      FilterSpec('short_name'),
                                      FilterSpec('long_name'))
    """
    def __init__(self, parentfield, *filterspecs):
        self.filterspecs = []
        for filterspec in filterspecs:
            fieldname = '{0}__{1}'.format(parentfield, filterspec.fieldname)
            self.filterspecs.append(FilterSpec(fieldname, filterspec.operations))

    def __iter__(self):
        for filterspec in self.filterspecs:
            for fieldoperation in filterspec:
                yield fieldoperation


class FilterSpecs(object):
    """ Container of :class:`FilterSpec` and :class:`ForeignFilterSpec`. """
    def __init__(self, *filterspecs):
        self.all_filters = set()
        self.pattern_filters = []
        for filterspec in filterspecs:
            for ispattern, fieldoperation in filterspec:
                if ispattern:
                    self.pattern_filters.append(fieldoperation)
                else:
                    self.all_filters.add(fieldoperation)

    def validate(self, filters):
        """
        Validate the given filters.

        :param filters: Dict where keys are filter fields.
        :throws FilterValidationError: If any of the ``filters`` are not in the
                filterspecs.
        """
        for filtername in filters:
            print filtername
            if not filtername in self.all_filters:
                valid = False
                if self.pattern_filters:
                    for patternfilterspec in self.pattern_filters:
                        if fnmatchcase(filtername, patternfilterspec):
                            valid = True
                if not valid:
                    raise FilterValidationError('{0} is not a valid filter.'.format(filtername))
