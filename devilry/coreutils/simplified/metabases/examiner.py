from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs


class SimplifiedExaminerMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Examiner object
    using the Simplified API """
    model = models.Examiner
    resultfields = FieldSpec('id',
                             'assignmentgroup')
    searchfields = FieldSpec()
    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('assignmentgroup'),
                          FilterSpec('assignmentgroup__parentnode'), # Assignment
                          FilterSpec('assignmentgroup__parentnode__parentnode'), # Period
                          FilterSpec('assignmentgroup__parentnode__parentnode__parentnode') # Subject
                         )
