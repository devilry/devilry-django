from ...simplified import simplified_modelapi, PermissionDenied, FieldSpec
from ..core import models


class PublishedWhereIsCandidateMixin(object):

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class Feedback(PublishedWhereIsCandidateMixin):

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
        _delivery_success = 'delivery__successful'

        model = models.Feedback
        resultfields = FieldSpec('id', 'format', 'text',
                                 period = [_period_short, _period_long, _period_id],
                                 subject = [_subject_long, _subject_short, _subject_id],
                                 assignment = [_assignment_short, _assignment_long, _assignment_id],
                                 delivery = [_delivery_time, _delivery_number, _delivery_success])
        searchfields = FieldSpec(_subject_short,
                                 _subject_long,
                                 _period_short,
                                 _period_long,
                                 _assignment_long,
                                 _assignment_short,
                                 _delivery_success,
                                 _delivery_number)
        methods = ['search', 'read']


@simplified_modelapi
class Delivery(PublishedWhereIsCandidateMixin):

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
        resultfields = FieldSpec('id', 'time_of_delivery', 'number', 'successful',
                                 period = [_period_short, _period_long, _period_id],
                                 subject = [_subject_long, _subject_short, _subject_id],
                                 assignment = [_assignment_short, _assignment_long, _assignment_id])
        searchfields = FieldSpec(
            _subject_short,
            _subject_long,
            _period_short,
            _period_long,
            _assignment_long,
            _assignment_short,
            'successful'
            )
        methods = ['search', 'read', 'delete']


@simplified_modelapi
class Assignment(PublishedWhereIsCandidateMixin):

        class Meta:

            _subject_long     = 'parentnode__parentnode__parentnode__long_name'
            _subject_short    = 'parentnode__parentnode__parentnode__short_name'
            _subject_id       = 'parentnode__parentnode__parentnode__id'

            _period_long      = 'parentnode__parentnode__long_name'
            _period_short     = 'parentnode__parentnode__short_name'
            _period_id        = 'parentnode__parentnode__id'

            model = models.Assignment
            resultfields = FieldSpec('id', 'format', 'text',
                                     period = [_period_short, _period_long, _period_id],
                                     subject = [_subject_long, _subject_short, _subject_id])
            searchfields = FieldSpec(
                _subject_short,
                _subject_long,
                _period_short,
                _period_long,
                )
            methods = ['search', 'read']


@simplified_modelapi
class Period(PublishedWhereIsCandidateMixin):

    class Meta:
        _subject_long     = 'parentnode__long_name'
        _subject_short    = 'parentnode__short_name'
        _subject_id       = 'parentnode__id'

        model = models.Period
        resultfields = FieldSpec('id', 'format', 'text',
                                 subject = [_subject_long, _subject_short, _subject_id])
        searchfields = FieldSpec(_subject_long, _subject_short)
        methods = ['search', 'read']


@simplified_modelapi
class Subject(PublishedWhereIsCandidateMixin):

    class Meta:
        model = models.Subject
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'periods')
        searchfields = FieldSpec('short_name', 'long_name', 'periods')
        methods = ['search', 'read']
