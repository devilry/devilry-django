from devilry.apps.core import models
from devilry.simplified import (FieldSpec, FilterSpec, FilterSpecs, OneToMany,
                                ForeignFilterSpec, boolConverter, intConverter, noCandidateIdConverter,
                                intOrNoneConverter, dateTimeConverter)



class SimplifiedAssignmentGroupMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for an AssignmentGroup object
    using the Simplified API """
    model = models.AssignmentGroup
    annotated_fields = ('latest_delivery_id', 'number_of_deliveries', 'latest_deadline_deadline', 'latest_deadline_id')
    resultfields = FieldSpec('id',
                             'name',
                             'is_open',
                             'parentnode',
                             'feedback',
                             'latest_delivery_id',
                             'latest_deadline_id',
                             'latest_deadline_deadline',
                             'number_of_deliveries',
                             candidates=[OneToMany('candidates', fields=['identifier', 'full_name', 'email'])],
                             feedback=['feedback__points',
                                       'feedback__grade',
                                       'feedback__is_passing_grade'],
                             feedback_rendered_view=['feedback__rendered_view'],
                             feedbackdelivery=['feedback__delivery__number',
                                               'feedback__delivery__time_of_delivery',
                                               'feedback__delivery__delivery_type',
                                               'feedback__delivery__deadline'],
                             assignment=['parentnode__long_name',
                                         'parentnode__short_name',
                                         'parentnode__anonymous',
                                         'parentnode__delivery_types',
                                         'parentnode__publishing_time'],
                             period=['parentnode__parentnode',
                                     'parentnode__parentnode__long_name',
                                     'parentnode__parentnode__short_name'],
                             subject=['parentnode__parentnode__parentnode',
                                      'parentnode__parentnode__parentnode__long_name',
                                      'parentnode__parentnode__parentnode__short_name']
                             )
    orderbyfields = ['candidates__identifier', 'candidates__full_name', 'candidates__email']
    searchfields = FieldSpec('name',
                             'candidates__identifier',
                             'candidates__full_name',
                             'candidates__email',
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
                          FilterSpec('is_open', type_converter=boolConverter),
                          FilterSpec('latest_deadline_deadline', type_converter=dateTimeConverter),
                          FilterSpec('number_of_deliveries', type_converter=intConverter),

                          # Feedback
                          FilterSpec('feedback', type_converter=intOrNoneConverter),
                          FilterSpec('feedback__points', type_converter=intConverter),
                          FilterSpec('feedback__is_passing_grade', type_converter=boolConverter),
                          FilterSpec('feedback__grade'),

                          FilterSpec('candidates__identifier', type_converter=noCandidateIdConverter),

                          # Latest delivery
                          FilterSpec('feedback__delivery__number', type_converter=intConverter),
                          FilterSpec('feedback__delivery__time_of_delivery', type_converter=dateTimeConverter),
                          FilterSpec('feedback__delivery__delivery_type', type_converter=intConverter),

                          ForeignFilterSpec('parentnode',  # Assignment
                                            FilterSpec('delivery_types'),
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode',  # Period
                                            FilterSpec('parentnode'),
                                            FilterSpec('start_time'),
                                            FilterSpec('end_time'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode__parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))
