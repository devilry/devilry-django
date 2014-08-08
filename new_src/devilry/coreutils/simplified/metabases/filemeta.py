from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs



class SimplifiedFileMetaMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a FileMeta object
    using the Simplified API """
    model = models.FileMeta
    resultfields = FieldSpec('filename',
                             'size',
                             'id',
                             'delivery',
                             subject=['delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id',
                                      'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name'],
                             period=['delivery__deadline__assignment_group__parentnode__parentnode__id',
                                     'delivery__deadline__assignment_group__parentnode__parentnode__short_name',
                                     'delivery__deadline__assignment_group__parentnode__parentnode__long_name'],
                             assignment=['delivery__deadline__assignment_group__parentnode__id',
                                         'delivery__deadline__assignment_group__parentnode__short_name',
                                         'delivery__deadline__assignment_group__parentnode__long_name'])
    searchfields = FieldSpec(
        'delivery__deadline__assignment_group__candidates__identifier',  # student in assignment_group
        'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name',  # subject
        'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name',  # subject
        'delivery__deadline__assignment_group__parentnode__parentnode__short_name',  # period
        'delivery__deadline__assignment_group__parentnode__parentnode__long_name',  # period
        'delivery__deadline__assignment_group__parentnode__short_name',  # assignment
        'delivery__deadline__assignment_group__parentnode__long_name',  # assignment
        )

    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('filename'),
                          FilterSpec('size'),
                          FilterSpec('delivery'))
