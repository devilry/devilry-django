class FilterValidationError(Exception):
    """ Raised when an invalid filter is given to
    :meth:`devilry.simplified.SimplifiedModelApi.search`. """

class FilterSpec(object):
    ALL_OPERATIONS = ('', 'exact', 'iexact',
                      'lt', 'gt', 'lte', 'gte',
                      'contains', 'icontains',
                      'startswith', 'endswith')

    def __init__(self, fieldname, operations=ALL_OPERATIONS):
        self.fieldname = fieldname
        self.operations = operations

    def __iter__(self):
        for operation in self.operations:
            if operation == '':
                yield self.fieldname
            else:
                yield '{0}__{1}'.format(self.fieldname, operation)

class ForeignFilterSpec():
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
    def __init__(self, *filterspecs):
        self.all_filters = set()
        for filterspec in filterspecs:
            self.all_filters.update(filterspec)

    def validate(self, filters):
        for filtername in filters:
            if not filtername in self.all_filters:
                raise FilterValidationError('{0} is not a valid filter.'.format(filtername))
