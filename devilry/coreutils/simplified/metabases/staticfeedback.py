from devilry.apps.core import models
from devilry.simplified import FieldSpec, FilterSpec, FilterSpecs, ForeignFilterSpec



class SimplifiedStaticFeedbackMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a StaticFeedback object
    using the Simplified API """
    model = models.StaticFeedback
    resultfields = FieldSpec('id',
                             'grade',
                             'is_passing_grade',
                             'saved_by',
                             'save_timestamp',
                             'delivery',
                             'rendered_view',
                             candidates=['delivery__deadline__assignment_group__candidates__identifier'],
                             period=['delivery__deadline__assignment_group__parentnode__parentnode__id',
                                     'delivery__deadline__assignment_group__parentnode__parentnode__short_name',
                                     'delivery__deadline__assignment_group__parentnode__parentnode__long_name'],
                             subject=['delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id',
                                      'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name'],
                             assignment=['delivery__deadline__assignment_group__parentnode__id',
                                         'delivery__deadline__assignment_group__parentnode__short_name',
                                         'delivery__deadline__assignment_group__parentnode__long_name'],
                             assignment_group=['delivery__deadline__assignment_group',
                                               'delivery__deadline__assignment_group__name'],
                             delivery=['delivery__time_of_delivery',
                                       'delivery__number',
                                       'delivery__delivered_by'])
    searchfields = FieldSpec('delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
                             'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name',
                             'delivery__deadline__assignment_group__parentnode__parentnode__short_name',
                             'delivery__deadline__assignment_group__parentnode__parentnode__long_name',
                             'delivery__deadline__assignment_group__parentnode__short_name',
                             'delivery__deadline__assignment_group__parentnode__long_name',
                             'delivery__number')
    filters = FilterSpecs(FilterSpec('id'),
                          FilterSpec('delivery'),
                          ForeignFilterSpec('delivery__deadline__assignment_group__parentnode__parentnode',  # Period
                                            FilterSpec('start_time'),
                                            FilterSpec('end_time')),
                         )

