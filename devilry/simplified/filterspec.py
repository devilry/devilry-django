from fnmatch import fnmatchcase
from django.db.models import Q


COMP_TO_DJANGO_MAP = {'exact': 'exact',
                      'iexact': 'exact',
                      '<': 'lt',
                      '>': 'gt',
                      '<=': 'lte',
                      '=>': 'gte',
                      'contains': 'contains',
                      'icontains': 'icontains',
                      'startswith': 'startswith',
                      'endswith': 'endswith'}


class FilterValidationError(Exception):
    """ Raised when an invalid filter is given to
    :meth:`devilry.simplified.SimplifiedModelApi.search`. """

class FilterSpec(object):
    """ Specifies that a specific field can be filtered, and what *comp* it can
    use. """
    def __init__(self, fieldname, supported_comp=('exact', 'iexact',
                                                 '<', '>', '<=', '=>',
                                                 'contains', 'icontains',
                                                 'startswith', 'endswith')):
        """
        :param fieldname: The field to allow filtering on.
        :param supported_comp: The allowed *comp* for this field.
        """
        self.fieldname = fieldname
        for comp in supported_comp:
            if not comp in COMP_TO_DJANGO_MAP:
                raise ValueError('A FieldSpec uses an invalid supported_cmp: {0}.'
                                 'Fieldname: {1}. All supported comps: '
                                 '{2}'.format(comp, fieldname,
                                              ','.join(COMP_TO_DJANGO_MAP.keys())))
        self.supported_comp = set(supported_comp)


    def _yield(self, value):
        return False, value

    def __iter__(self):
        for comp in self.supported_comp:
            if comp == '':
                yield self._yield(self.fieldname)
            else:
                yield self._yield('{0}__{1}'.format(self.fieldname, comp))

    def to_django_qry(self, filterdict):
        try:
            comp = filterdict['comp']
            value = filterdict['value']
        except KeyError, e:
            raise FilterValidationError('Invalid filter: {0}'.format(filterdict))
        else:
            if not comp in self.supported_comp:
                raise FilterValidationError('Invalid filter: {0}. {1} is not a supported "comp".'.format(filterdict, comp))
            djangocomp = COMP_TO_DJANGO_MAP[comp]
            filterfieldname = '{0}__{1}'.format(self.fieldname, djangocomp)
            qryparam = {filterfieldname: value}
            return Q(**qryparam)

    def aslist(self):
        return [self]




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
            self.filterspecs.append(FilterSpec(fieldname, filterspec.supported_comp))

    def aslist(self):
        return self.filterspecs

class FilterSpecs(object):
    """ Container of :class:`FilterSpec` and :class:`ForeignFilterSpec`. """
    def __init__(self, *filterspecs_and_foreignkeyfilterspecs):
        self.all_filters = set()
        self.filterspecs = {}
        for filterspec_or_fkfilterspec in filterspecs_and_foreignkeyfilterspecs:
            for filterspec in filterspec_or_fkfilterspec.aslist():
                self.filterspecs[filterspec.fieldname] = filterspec

    def parse(self, filters):
        """
        Validate the given filters and translate them into a Django query.

        :param filters: A list of filters on the following format::

            [{'field': 'myfieldname', 'comp': '>', 'value': 30},
             {'field': 'myotherfieldname', 'comp': '=', 'value': 'myname'}]

        :throws FilterValidationError: If any of the ``filters`` are not in the
                filterspecs.
        """
        qry = Q()
        for filterdict in filters:
            try:
                filtername = filterdict['field']
                filterspec = self.filterspecs[filtername]
            except KeyError, e:
                raise FilterValidationError('Invalid filter: {0}'.format(filterdict))
            except TypeError, e:
                raise FilterValidationError('Invalid filter: {0}'.format(filterdict))
            else:
                qry &= filterspec.to_django_qry(filterdict)
                #if self.pattern_filters:
                    #for patternfilterspec in self.pattern_filters:
                        #if fnmatchcase(filtername, patternfilterspec):
                            #valid = True
        return qry
