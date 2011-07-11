from ...simplified import (simplified_modelapi, SimplifiedModelApi,
                           PermissionDenied, FieldSpec, FilterSpec, FilterSpecs, PatternFilterSpec, ForeignFilterSpec)
from ..core import models


class SimplifiedNodeMetaMixin(object):
    model = models.Node
    resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode')
    searchfields = FieldSpec('short_name', 'long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          PatternFilterSpec('parentnode__*short_name'),
                          PatternFilterSpec('parentnode__*long_name'),
                          PatternFilterSpec('parentnode__*id'))


class SimplifiedSubjectMetaMixin(object):
    model = models.Subject
    resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode')
    searchfields = FieldSpec('short_name', 'long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          ForeignFilterSpec('parentnode',  # Node
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))


class SimplifiedPeriodMetaMixin(object):
    model = models.Period
    resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode',
                             'start_time', 'end_time',
                             subject=['parentnode__short_name', 'parentnode__long_name'])
    searchfields = FieldSpec('short_name', 'long_name', 'parentnode__short_name',
                             'parentnode__long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          ForeignFilterSpec('parentnode',  # Subject
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))


class SimplifiedAssignmentMetaMixin(object):
    model = models.Assignment
    resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode', 'publishing_time',
                             period=['parentnode__short_name',
                                     'parentnode__long_name',
                                     'parentnode__parentnode'],
                             subject=['parentnode__parentnode__short_name',
                                      'parentnode__parentnode__long_name'],
                             pointfields=['anonymous', 'must_pass', 'maxpoints',
                                          'attempts'])
    searchfields = FieldSpec('short_name', 'long_name',
                             'parentnode__short_name',
                             'parentnode__long_name',
                             'parentnode__parentnode__short_name',
                             'parentnode__parentnode__long_name')
    filters = FilterSpecs(FilterSpec('parentnode'),
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          # Period
                          ForeignFilterSpec('parentnode',
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          # Subject
                          ForeignFilterSpec('parentnode__parentnode',
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))


class SimplifiedAssignmentGroupMetaMixin(object):
    model = models.AssignmentGroup
    resultfields = FieldSpec('id', 'name', 'is_open', 'status', 'parentnode',
                             users=['examiners__username', 'candidates__identifier'],
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
                          FilterSpec('short_name'),
                          FilterSpec('long_name'),
                          ForeignFilterSpec('parentnode',  # Assignment
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode',  # Period
                                            FilterSpec('paretnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')),
                          ForeignFilterSpec('parentnode__parentnode__parentnode',  # Subject
                                            FilterSpec('parentnode'),
                                            FilterSpec('short_name'),
                                            FilterSpec('long_name')))


class SimplifiedDeadlineMetaMixin(object):
    model = models.Deadline
    resultfields = FieldSpec('text', 'deadline', 'assignment_group', 'status', 'feedbacks_published', 'id',
                             subject=['assignment_group__parentnode__parentnode__parentnode__long_name',
                                      'assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'assignment_group__parentnode__parentnode__parentnode__id'],
                             period=['assignment_group__parentnode__parentnode__long_name',
                                     'assignment_group__parentnode__parentnode__short_name',
                                     'assignment_group__parentnode__parentnode__id'],
                             assignment=['assignment_group__parentnode__long_name',
                                         'assignment_group__parentnode__short_name',
                                         'assignment_group__parentnode__id']
                             )
    searchfields = FieldSpec(
        #'delivered_by',
        'assignment_group__candidates__identifier',
        'assignment_group__parentnode__short_name',  # Name of assignment
        'assignment_group__parentnode__long_name',  # Name of assignment
        'assignment_group__parentnode__parentnode__short_name',  # Name of period
        'assignment_group__parentnode__parentnode__long_name',  # Name of period
        'assignment_group__parentnode__parentnode__parentnode__short_name',  # Name of subject
        'assignment_group__parentnode__parentnode__parentnode__long_name'  # Name of subject
        )  # What should search() search from


class SimplifiedDeliveryMetaMixin(object):
    model = models.Delivery
    resultfields = FieldSpec('id', 'number', 'time_of_delivery', 'assignment_group',
                             assignment_group=['assignment_group', 'assignment_group__name'],
                             assignment=['assignment_group__parentnode',
                                         'assignment_group__parentnode__long_name',
                                         'assignment_group__parentnode__short_name'],
                             period=['assignment_group__parentnode__parentnode',
                                     'assignment_group__parentnode__parentnode__long_name',
                                     'assignment_group__parentnode__parentnode__short_name'],
                             subject=['assignment_group__parentnode__parentnode__parentnode',
                                      'assignment_group__parentnode__parentnode__parentnode__long_name',
                                      'assignment_group__parentnode__parentnode__parentnode__short_name'])
    searchfields = FieldSpec('number',
                             # assignmentgroup
                             'assignment_group__name',
                             'assignment_group__examiners__username',
                             'assignment_group__candidates__identifier',
                             'assignment_group__examiners__username',
                             'assignment_group__candidates__identifier',
                             # assignment
                             'assignment_group__parentnode__long_name',
                             'assignment_group__parentnode__short_name',
                             # period
                             'assignment_group__parentnode__parentnode__long_name',
                             'assignment_group__parentnode__parentnode__short_name',
                             # subject
                             'assignment_group__parentnode__parentnode__parentnode__long_name',
                             'assignment_group__parentnode__parentnode__parentnode__short_name')


class SimplifiedStaticFeedbackMetaMixin(object):
    _subject_long     = 'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'
    _subject_short    = 'delivery__assignment_group__parentnode__parentnode__parentnode__short_name'
    _subject_id       = 'delivery__assignment_group__parentnode__parentnode__parentnode__id'

    _period_long      = 'delivery__assignment_group__parentnode__parentnode__long_name'
    _period_short     = 'delivery__assignment_group__parentnode__parentnode__short_name'
    _period_id        = 'delivery__assignment_group__parentnode__parentnode__id'

    _assignment_long  = 'delivery__assignment_group__parentnode__long_name'
    _assignment_short = 'delivery__assignment_group__parentnode__short_name'
    _assignment_id    = 'delivery__assignment_group__parentnode__id'

    _delivery_time    = 'delivery__time_of_delivery'
    _delivery_number  = 'delivery__number'
    _delivery_delivered_by = 'delivery__delivered_by'
    _delivery_after_deadline = 'delivery__after_deadline'

    model = models.StaticFeedback
    resultfields = FieldSpec('id', 'grade', 'points', 'is_passing_grade',
                             period=[_period_short, _period_long, _period_id],
                             subject=[_subject_long, _subject_short, _subject_id],
                             assignment=[_assignment_short, _assignment_long, _assignment_id],
                             delivery=[_delivery_time, _delivery_number, ])
    searchfields = FieldSpec(_subject_short,
                             _subject_long,
                             _period_short,
                             _period_long,
                             _assignment_long,
                             _assignment_short,
                             _delivery_number,
                             )


class SimplifiedFileMetaMetaMixin(object):
    model = models.FileMeta
    resultfields = FieldSpec('filename', 'size', 'id',
                             subject=['delivery__assignment_group__parentnode__parentnode__parentnode__long_name',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                                      'delivery__assignment_group__parentnode__parentnode__parentnode__id'],
                             period=['delivery__assignment_group__parentnode__parentnode__long_name',
                                     'delivery__assignment_group__parentnode__parentnode__short_name',
                                     'delivery__assignment_group__parentnode__parentnode__id'],
                             assignment=['delivery__assignment_group__parentnode__long_name',
                                         'delivery__assignment_group__parentnode__short_name',
                                         'delivery__assignment_group__parentnode__id']
                             )
    searchfields = FieldSpec(
        # delivery__delivered_by
        'delivery__assignment_group__candidates__identifier',  # student in assignment_group
        'delivery__assignment_group__parentnode__parentnode__parentnode__long_name',  # subject
        'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',  # subject
        'delivery__assignment_group__parentnode__parentnode__long_name',  # period
        'delivery__assignment_group__parentnode__parentnode__short_name',  # period
        'delivery__assignment_group__parentnode__long_name',  # assignment
        'delivery__assignment_group__parentnode__short_name',  # assignment
        )


class PublishedWhereIsCandidateMixin(SimplifiedModelApi):

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsCandidateMixin):
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read', 'delete']


@simplified_modelapi
class SimplifiedAssignmentGroup(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedAssignmentMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedPeriodMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsCandidateMixin, SimplifiedModelApi):
    class Meta(SimplifiedSubjectMetaMixin):
        methods = ['search', 'read']
