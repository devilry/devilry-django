import re
from datetime import datetime
from django.db.models import Q

from exceptions import FilterValidationError


COMP_TO_DJANGO_MAP = {'exact': 'exact',
                      'iexact': 'exact',
                      '<': 'lt',
                      '>': 'gt',
                      '<=': 'lte',
                      '>=': 'gte',
                      'contains': 'contains',
                      'icontains': 'icontains',
                      'startswith': 'startswith',
                      'endswith': 'endswith'}


def _in_both(lstA, lstB):
    """
    Return the first item which is in both ``lstA`` and ``lstB``, or ``None``
    if the two lists do not contain any equal items.
    """
    for item in lstA:
        if item in lstB:
            return item
    return None


def nullConverter(value):
    return value
def boolConverter(value):
    if isinstance(value, bool):
        return value
    else:
        return value.lower() == 'yes'
def intConverter(value):
    return int(value)
def intOrNoneConverter(value):
    if isinstance(value, basestring) and value.lower() == 'none':
        return None
    return int(value)
def stringOrNoneConverter(value):
    if isinstance(value, basestring) and value.lower() == 'none':
        return None
    return value
def noCandidateIdConverter(value):
    if isinstance(value, basestring) and value.lower() == 'none':
        return 'candidate-id missing'
    return value
def dateTimeConverter(value):
    return datetime.strptime(str(value), '%Y-%m-%dT%H:%M:%S')


class FilterSpec(object):
    """ Specifies that a specific field can be filtered, and what *comp* it can
    use. """
    def __init__(self, fieldname,
                 supported_comp=('exact', 'iexact',
                                 '<', '>', '<=', '>=',
                                 'contains', 'icontains',
                                 'startswith', 'endswith'),
                 type_converter=nullConverter):
        """
        :param fieldname: The field to allow filtering on.
        :param supported_comp: The allowed *comp* for this field.
        """
        self.type_converter = type_converter
        self.fieldname = fieldname
        for comp in supported_comp:
            if not comp in COMP_TO_DJANGO_MAP:
                raise ValueError('FilterSpec uses an invalid supported_cmp: {0}.'
                                 'Fieldname: {1}. All supported comps: '
                                 '{2}'.format(comp, fieldname,
                                              ','.join(COMP_TO_DJANGO_MAP.keys())))
        self.supported_comp = set(supported_comp)

    def to_django_qry(self, filterdict):
        try:
            comp = filterdict['comp']
            value = filterdict['value']
            fieldname = filterdict['field']
        except KeyError, e:
            try:
                comp = 'exact'
                value = filterdict['value']
                fieldname = filterdict['property']
            except KeyError, e:
                raise FilterValidationError('Invalid filter: {0}'.format(filterdict))

        if isinstance(value, basestring) and value.strip() == '':
            return None
        if not comp in self.supported_comp:
            raise FilterValidationError('Invalid filter: {0}. {1} is not a supported "comp".'.format(filterdict, comp))
        try:
            value = self.type_converter(value)
        except ValueError, e:
            raise FilterValidationError('Value has invalid type for field {0}: {1}'.format(fieldname, value))
        djangocomp = COMP_TO_DJANGO_MAP[comp]
        filterfieldname = '{0}__{1}'.format(fieldname, djangocomp)
        qryparam = {filterfieldname: value}
        #print qryparam
        return Q(**qryparam)

    def aslist(self):
        return [self]




class PatternFilterSpec(FilterSpec):
    """
    Pattern based field spec.

    **NOTE**: Should only be used when _really_ required, since it is less
    secure and slows down filter validation (which is done on each search()).
    """
    def __init__(self, *args, **kwargs):
        super(PatternFilterSpec, self).__init__(*args, **kwargs)
        self.fieldpatt = re.compile(self.fieldname)

    def matches(self, fieldname):
        return bool(self.fieldpatt.match(fieldname))


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
        self.filterspecs = {}
        self.patternfilterspecs = []
        for filterspec_or_fkfilterspec in filterspecs_and_foreignkeyfilterspecs:
            for filterspec in filterspec_or_fkfilterspec.aslist():
                if isinstance(filterspec, PatternFilterSpec):
                    self.patternfilterspecs.append(filterspec)
                else:
                    if filterspec.fieldname in self.filterspecs:
                        raise ValueError('A FilterSpec with fieldname "{0}" is '
                                         'already in the FilterSpecs.'.format(filterspec.fieldname))
                    self.filterspecs[filterspec.fieldname] = filterspec
        self.validate_no_dups_with_patterns()

    def validate_no_dups_with_patterns(self):
        for filterspec in self.filterspecs.itervalues():
            for patternfilterpec in self.patternfilterspecs:
                if patternfilterpec.matches(filterspec.fieldname):
                    raise ValueError('The "{0}" pattern matches the non-pattern '
                                     'filterspec: {1}'.format(patternfilterpec.fieldname,
                                                              filterspec.fieldname))

    def find_filterspec(self, fieldname):
        try:
            return self.filterspecs[fieldname]
        except KeyError, e:
            for patternfilterpec in self.patternfilterspecs:
                if patternfilterpec.matches(fieldname):
                    return patternfilterpec
            raise

    def parse(self, filters):
        """
        Validate the given filters and translate them into a Django query.

        :param filters:
            A list of filters on the following format::

                [{'field': 'myfieldname', 'comp': '>', 'value': 30},
                 {'field': 'myotherfieldname', 'comp': '=', 'value': 'myname'}]

        :throws FilterValidationError: If any of the ``filters`` are not in the
                filterspecs.
        """
        qry = Q()
        for filterdict in filters:
            try:
                fieldname = filterdict['field']
            except KeyError, e:
                try:
                    fieldname = filterdict['property']
                except KeyError, e:
                    raise FilterValidationError('Invalid filter: {0}. No "field" specified.'.format(filterdict))

            try:
                filterspec = self.find_filterspec(fieldname)
            except KeyError, e:
                fieldnames = ', '.join(self.filterspecs.keys())
                raise FilterValidationError('Invalid filter fieldname {0} in: {1}. Available filter fieldnames: {2}'.format(fieldname, filterdict, fieldnames))
            else:
                qrysegment = filterspec.to_django_qry(filterdict)
                if qrysegment != None:
                    qry &= filterspec.to_django_qry(filterdict)
        return qry

    def __add__(self, other):

        # Make sure other does not share any items with self
        inboth = _in_both(self.filterspecs.keys(), other.filterspecs.keys())
        if inboth:
            raise ValueError("{0} already in filterspec.".format(inboth))
        inboth = _in_both([p.fieldname for p in self.patternfilterspecs],
                          [p.fieldname for p in other.patternfilterspecs])
        if inboth:
            raise ValueError("{0} already in filterspec.".format(inboth))

        # Create a new FilterSpecs from self and other
        filterspecs = FilterSpecs()
        filterspecs.filterspecs = self.filterspecs.copy()
        filterspecs.filterspecs.update(other.filterspecs)
        filterspecs.patternfilterspecs = list(self.patternfilterspecs) + list(other.patternfilterspecs)
        filterspecs.validate_no_dups_with_patterns()
        return filterspecs

    def __nonzero__(self):
        return len(self.filterspecs) > 0 or len(self.patternfilterspecs) > 0


    def iterfieldnames(self):
        """
        Iterate over all fieldnames in this FilterSpecs. Used in
        @simplified_modelapi to validate the fields in this FilterSpecs. Note
        that PatternFilterSpec are not validated.
        """
        return self.filterspecs.keys().__iter__()
