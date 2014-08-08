from devilry.simplified import (FieldSpec, FilterSpec, FilterSpecs)


class SimplifiedAbstractApplicationKeyValueMixin(object):
    resultfields = FieldSpec('id', 'application', 'key', 'value')
    searchfields = FieldSpec('application', 'key', 'value')
    editablefields = ('application', 'key', 'value')
    filters = FilterSpecs(FilterSpec('id', supported_comp=('exact',)),
                          FilterSpec('application', supported_comp=('exact',)),
                          FilterSpec('key', supported_comp=('exact',)))
