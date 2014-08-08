from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedPeriodMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Period object
    using the Simplified API """
    model = models.Period
    resultfields = FieldSpec('id',
                             'parentnode',
                             'short_name',
                             'long_name',
                             'start_time',
                             'end_time',
                             subject=['parentnode__short_name',
                                      'parentnode__long_name'])
    searchfields = FieldSpec('short_name',
                             'long_name',
                             'parentnode__short_name',
                             'parentnode__long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          FilterSpec('start_time'),
                          FilterSpec('end_time'),
                          ForeignFilterSpec('parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
