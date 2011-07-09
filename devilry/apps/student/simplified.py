from ...simplified import (simplified_modelapi, SimplifiedModelApi,
                           PermissionDenied, FieldSpec)
from ..core import models

# TODO: Add SimplifiedDeadline
# TODO: Add SimplifiedNode


class PublishedWhereIsCandidateMixin(object):

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:

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
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:

        _subject_long     = 'assignment_group__parentnode__parentnode__parentnode__long_name'
        _subject_short    = 'assignment_group__parentnode__parentnode__parentnode__short_name'
        _subject_id       = 'assignment_group__parentnode__parentnode__parentnode__id'

        _period_long      = 'assignment_group__parentnode__parentnode__long_name'
        _period_short     = 'assignment_group__parentnode__parentnode__short_name'
        _period_id        = 'assignment_group__parentnode__parentnode__id'

        _assignment_long  = 'assignment_group__parentnode__long_name'
        _assignment_short = 'assignment_group__parentnode__short_name'
        _assignment_id    = 'assignment_group__parentnode__id'

        model = models.Delivery
        resultfields = FieldSpec('id', 'time_of_delivery', 'number',
                                 period=[_period_short, _period_long, _period_id],
                                 subject=[_subject_long, _subject_short, _subject_id],
                                 assignment=[_assignment_short, _assignment_long, _assignment_id])
        searchfields = FieldSpec(
            _subject_short,
            _subject_long,
            _period_short,
            _period_long,
            _assignment_long,
            _assignment_short,
            )
        methods = ['search', 'read', 'delete']


@simplified_modelapi
class SimplifiedAssignmentGroup(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:

        _subject_long     = 'parentnode__parentnode__parentnode__long_name'
        _subject_short    = 'parentnode__parentnode__parentnode__short_name'
        _subject_id       = 'parentnode__parentnode__parentnode__id'

        _period_long      = 'parentnode__parentnode__long_name'
        _period_short     = 'parentnode__parentnode__short_name'
        _period_id        = 'parentnode__parentnode__id'

        _assignment_long  = 'parentnode__long_name'
        _assignment_short = 'parentnode__short_name'
        _assignment_id    = 'parentnode__id'

        model = models.AssignmentGroup
        resultfields = FieldSpec(_assignment_long, _assignment_short, _assignment_id,
                                 period=[_period_short, _period_long, _period_id],
                                 subject=[_subject_long, _subject_short, _subject_id],
                                 assignment=[_assignment_short, _assignment_long, _assignment_id])
        searchfields = FieldSpec(
            _subject_short,
            _subject_long,
            _period_short,
            _period_long,
            _assignment_long,
            _assignment_short,
            )
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedAssignment(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:

        _subject_long     = 'parentnode__parentnode__long_name'
        _subject_short    = 'parentnode__parentnode__short_name'
        _subject_id       = 'parentnode__parentnode__id'

        _period_long      = 'parentnode__long_name'
        _period_short     = 'parentnode__short_name'
        _period_id        = 'parentnode__id'

        _assignment_long  = 'long_name'
        _assignment_short = 'short_name'
        _assignment_id    = 'id'

        model = models.Assignment
        resultfields = FieldSpec(_assignment_long, _assignment_short, _assignment_id,
                                 period=[_period_short, _period_long, _period_id],
                                 subject=[_subject_long, _subject_short, _subject_id])
        searchfields = FieldSpec(
            _subject_short,
            _subject_long,
            _period_short,
            _period_long,
            _assignment_short,
            _assignment_long
            )
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:
        _subject_long     = 'parentnode__long_name'
        _subject_short    = 'parentnode__short_name'
        _subject_id       = 'parentnode__id'

        model = models.Period
        resultfields = FieldSpec('long_name', 'short_name', 'id',
                                 subject=[_subject_long, _subject_short, _subject_id])
        searchfields = FieldSpec('long_name', 'short_name', 'id',
                                 _subject_long, _subject_short)
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedSubject(SimplifiedModelApi, PublishedWhereIsCandidateMixin):

    class Meta:
        model = models.Subject
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['search', 'read']
