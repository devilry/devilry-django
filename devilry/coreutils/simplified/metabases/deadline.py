from devilry.apps.core import models
from devilry.simplified import (FieldSpec, FilterSpec, FilterSpecs,
                                ForeignFilterSpec)



class SimplifiedDeadlineMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Deadline object
    using the Simplified API """
    model = models.Deadline
    annotated_fields = ('number_of_deliveries',)
    resultfields = FieldSpec('id',
                             'text',
                             'deadline',
                             'assignment_group',
                             'number_of_deliveries',
                             'feedbacks_published',
                             subject=['assignment_group__parentnode__parentnode__parentnode__id',
                                      'assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'assignment_group__parentnode__parentnode__parentnode__long_name'],
                             period=['assignment_group__parentnode__parentnode__id',
                                     'assignment_group__parentnode__parentnode__short_name',
                                     'assignment_group__parentnode__parentnode__long_name'],
                             assignment=['assignment_group__parentnode__id',
                                         'assignment_group__parentnode__delivery_types',
                                         'assignment_group__parentnode__short_name',
                                         'assignment_group__parentnode__long_name'],
                             assignment_group=['assignment_group__name', 'assignment_group__is_open'],
                             assignment_group_users=['assignment_group__candidates__identifier']
                             )
    searchfields = FieldSpec(
        'assignment_group__candidates__identifier',
        'assignment_group__parentnode__short_name',  # Name of assignment
        'assignment_group__parentnode__long_name',  # Name of assignment
        'assignment_group__parentnode__parentnode__short_name',  # Name of period
        'assignment_group__parentnode__parentnode__long_name',  # Name of period
        'assignment_group__parentnode__parentnode__parentnode__short_name',  # Name of subject
        'assignment_group__parentnode__parentnode__parentnode__long_name'  # Name of subject
        )
    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('deadline'),
                          FilterSpec('assignment_group'),
                          FilterSpec('number_of_deliveries'),
                          ForeignFilterSpec('assignment_group',  # Assignment
                                            FilterSpec('is_open'),
                                            FilterSpec('name')),
                          ForeignFilterSpec('assignment_group__parentnode',  # Assignment
                                            FilterSpec('delivery_types'),
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('assignment_group__parentnode__parentnode',  # Period
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('assignment_group__parentnode__parentnode__parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
