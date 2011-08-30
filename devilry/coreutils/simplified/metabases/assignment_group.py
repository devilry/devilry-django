from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedAssignmentGroupMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for an AssignmentGroup object
    using the Simplified API """
    model = models.AssignmentGroup
    annotated_fields = ('latest_delivery_id', 'number_of_deliveries', 'latest_deadline_deadline', 'latest_deadline_id')
    resultfields = FieldSpec('id',
                             'name',
                             'is_open',
                             'status',
                             'parentnode',
                             'feedback',
                             'latest_delivery_id',
                             'latest_deadline_id',
                             'latest_deadline_deadline',
                             'number_of_deliveries',
                             users=['examiners__username',
                                    'candidates__identifier'],
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
                                         'parentnode__publishing_time'],
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
                          FilterSpec('is_open'),
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
