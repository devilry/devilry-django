from ..core import models
from ...simplified import FieldSpec, FilterSpec, FilterSpecs, PatternFilterSpec, ForeignFilterSpec


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
                          ForeignFilterSpec('parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))


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
                                          'maxpoints',
                                          'attempts'])
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
                             users=['examiners__username',
                                    'candidates__identifier'],
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


class SimplifiedDeadlineMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Deadline object
    using the Simplified API """
    model = models.Deadline
    resultfields = FieldSpec('id',
                             'text',
                             'deadline',
                             'assignment_group',
                             'status',
                             'feedbacks_published',
                             subject=['assignment_group__parentnode__parentnode__parentnode__id',
                                      'assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'assignment_group__parentnode__parentnode__parentnode__long_name'],
                             period=['assignment_group__parentnode__parentnode__id',
                                     'assignment_group__parentnode__parentnode__short_name',
                                     'assignment_group__parentnode__parentnode__long_name'],
                             assignment=['assignment_group__parentnode__id',
                                         'assignment_group__parentnode__short_name',
                                         'assignment_group__parentnode__long_name']
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


class SimplifiedDeliveryMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a Delivery object
    using the Simplified API """
    model = models.Delivery
    resultfields = FieldSpec('id',
                             'number',
                             'time_of_delivery',
                             'assignment_group',
                             assignment_group=['assignment_group',
                                               'assignment_group__name'],
                             assignment=['assignment_group__parentnode',
                                         'assignment_group__parentnode__short_name',
                                         'assignment_group__parentnode__long_name'],
                             period=['assignment_group__parentnode__parentnode',
                                     'assignment_group__parentnode__parentnode__short_name',
                                     'assignment_group__parentnode__parentnode__long_name'],
                             subject=['assignment_group__parentnode__parentnode__parentnode',
                                      'assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'assignment_group__parentnode__parentnode__parentnode__long_name'])
    searchfields = FieldSpec('number',
                             # assignmentgroup
                             'assignment_group__name',
                             'assignment_group__examiners__username',
                             'assignment_group__candidates__identifier',
                             # assignment
                             'assignment_group__parentnode__short_name',
                             'assignment_group__parentnode__long_name',
                             # period
                             'assignment_group__parentnode__parentnode__short_name',
                             'assignment_group__parentnode__parentnode__long_name',
                             # subject
                             'assignment_group__parentnode__parentnode__parentnode__short_name',
                             'assignment_group__parentnode__parentnode__parentnode__long_name')


class SimplifiedStaticFeedbackMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a StaticFeedback object
    using the Simplified API """
    model = models.StaticFeedback
    resultfields = FieldSpec('id',
                             'grade',
                             'is_passing_grade',
                             'saved_by',
                             'delivery',
                             'rendered_view',
                             #'delivery__assignment_group__examiners__username',
                             period=['delivery__assignment_group__parentnode__parentnode__id',
                                     'delivery__assignment_group__parentnode__parentnode__short_name',
                                     'delivery__assignment_group__parentnode__parentnode__long_name'],
                             subject=['delivery__assignment_group__parentnode__parentnode__parentnode__id',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'],
                             assignment=['delivery__assignment_group__parentnode__id',
                                         'delivery__assignment_group__parentnode__short_name',
                                         'delivery__assignment_group__parentnode__long_name'],
                             delivery=['delivery__time_of_delivery',
                                       'delivery__number',
                                       'delivery__delivered_by'])
    searchfields = FieldSpec('delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                             'delivery__assignment_group__parentnode__parentnode__parentnode__long_name',
                             'delivery__assignment_group__parentnode__parentnode__short_name',
                             'delivery__assignment_group__parentnode__parentnode__long_name',
                             'delivery__assignment_group__parentnode__short_name',
                             'delivery__assignment_group__parentnode__long_name',
                             'delivery__number',
                             'delivery__assignment_group__examiners__username',
                             )


class SimplifiedFileMetaMetaMixin(object):
    """ Defines the django model to be used, resultfields returned by
    search and which fields can be used to search for a FileMeta object
    using the Simplified API """
    model = models.FileMeta
    resultfields = FieldSpec('filename',
                             'size',
                             'id',
                             subject=['delivery__assignment_group__parentnode__parentnode__parentnode__id',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'],
                             period=['delivery__assignment_group__parentnode__parentnode__id',
                                     'delivery__assignment_group__parentnode__parentnode__short_name',
                                     'delivery__assignment_group__parentnode__parentnode__long_name'],
                             assignment=['delivery__assignment_group__parentnode__id',
                                         'delivery__assignment_group__parentnode__short_name',
                                         'delivery__assignment_group__parentnode__long_name'])
    searchfields = FieldSpec(
        'delivery__assignment_group__candidates__identifier',  # student in assignment_group
        'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',  # subject
        'delivery__assignment_group__parentnode__parentnode__parentnode__long_name',  # subject
        'delivery__assignment_group__parentnode__parentnode__short_name',  # period
        'delivery__assignment_group__parentnode__parentnode__long_name',  # period
        'delivery__assignment_group__parentnode__short_name',  # assignment
        'delivery__assignment_group__parentnode__long_name',  # assignment
        )
