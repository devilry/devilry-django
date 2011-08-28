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
                             period=['parentnode__short_name',
                                     'parentnode__long_name',
                                     'parentnode__parentnode'],
                             subject=['parentnode__parentnode__short_name',
                                      'parentnode__parentnode__long_name'],
                             pointfields=['anonymous',
                                          'must_pass',
                                          'maxpoints'])
    searchfields = FieldSpec('short_name',
                             'long_name',
                             'parentnode__short_name',
                             'parentnode__long_name',
                             'parentnode__parentnode__short_name',
                             'parentnode__parentnode__long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          # Period
                          ForeignFilterSpec('parentnode',
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          # Subject
                          ForeignFilterSpec('parentnode__parentnode',
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
