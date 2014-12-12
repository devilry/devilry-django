from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec


class SimplifiedCandidateMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Candidate object
    using the Simplified API """
    model = models.Candidate
    resultfields = FieldSpec('id',
                             'identifier',
                             'full_name',
                             'email',
                             'assignment_group')
    searchfields = FieldSpec('identifier')
    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('assignment_group'),
                          FilterSpec('assignment_group__parentnode'), # Assignment
                          FilterSpec('assignment_group__parentnode__parentnode'), # Period
                          FilterSpec('assignment_group__parentnode__parentnode__parentnode') # Subject
                         )
