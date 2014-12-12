from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedSubjectMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Subject object
    using the Simplified API """
    model = models.Subject
    resultfields = FieldSpec('id',
                             'parentnode',
                             'short_name',
                             'long_name',
                             )
    searchfields = FieldSpec('short_name',
                             'long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          ForeignFilterSpec('parentnode',  # Node
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
