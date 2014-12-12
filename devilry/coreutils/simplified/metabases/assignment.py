from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedAssignmentMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for an Assignment object
    using the Simplified API """
    model = models.Assignment
    resultfields = FieldSpec('id',
                             'parentnode',
                             'short_name',
                             'long_name',
                             'publishing_time',
                             'delivery_types',
                             'anonymous',
                             'scale_points_percent',
                             period=['parentnode__short_name',
                                     'parentnode__long_name',
                                     'parentnode__start_time',
                                     'parentnode__end_time',
                                     'parentnode__parentnode'],
                             subject=['parentnode__parentnode__short_name',
                                      'parentnode__parentnode__long_name']
                            )
    searchfields = FieldSpec('short_name',
                             'long_name',
                             'parentnode__short_name',
                             'parentnode__long_name',
                             'parentnode__parentnode__short_name',
                             'parentnode__parentnode__long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          FilterSpec('delivery_types'),
                          FilterSpec('anonymous'),
                          # Period
                          ForeignFilterSpec('parentnode',
                                            FilterSpec('parentnode'),
                                            FilterSpec('start_time'),
                                            FilterSpec('end_time'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          # Subject
                          ForeignFilterSpec('parentnode__parentnode',
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
