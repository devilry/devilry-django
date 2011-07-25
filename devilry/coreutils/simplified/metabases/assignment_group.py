from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedAssignmentGroupMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for an AssignmentGroup object
    using the Simplified API """
    model = models.AssignmentGroup
    resultfields = FieldSpec('id',
                             'name',
                             'is_open',
                             'status',
                             'parentnode',
                             'feedback',
                             users=['examiners__username',
                                    'candidates__identifier'],
                             feedback=['feedback__points',
                                       'feedback__grade',
                                       'feedback__is_passing_grade',
                                       'feedback__rendered_view'],
                             assignment=['parentnode__long_name',
                                         'parentnode__short_name'],
                             period=['parentnode__parentnode',
                                     'parentnode__parentnode__long_name',
                                     'parentnode__parentnode__short_name'],
                             subject=['parentnode__parentnode__parentnode',
                                      'parentnode__parentnode__parentnode__long_name',
                                      'parentnode__parentnode__parentnode__short_name']
                             )
    searchfields = FieldSpec('name',
                             'examiners__username',
                             'candidates__identifier',
                             # assignment
                             'parentnode__long_name',
                             'parentnode__short_name',
                             # period
                             'parentnode__parentnode__long_name',
                             'parentnode__parentnode__short_name',
                             # subject
                             'parentnode__parentnode__parentnode__long_name',
                             'parentnode__parentnode__parentnode__short_name',
                             )
    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('parentnode'),
                          ForeignFilterSpec('parentnode',  # Assignment
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode',  # Period
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode__parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
