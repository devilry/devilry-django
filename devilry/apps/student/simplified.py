from ...simplified import simplified_api, PermissionDenied
from ..core import models


class PublishedWhereIsCandidateMixin(object):

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_api
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
        resultfields = {
            '__BASE__'   : ['id', 'time_of_delivery', 'number', 'successful'],
            'period'     : [_period_short, _period_long, _period_id],
            'subject'    : [_subject_long, _subject_short, _subject_id],
            'assignment' : [_assignment_short, _assignment_long, _assignment_id],
            }
        searchfields = [_subject_short,
                        _subject_long,
                        _period_short,
                        _period_long,
                        _assignment_long,
                        _assignment_short,
                        'successful']
        methods = ['search', 'read', 'delete']


@simplified_api
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
        resultfields = {
            '__BASE__'   : ['id', 'format', 'text'],
            'period'     : [_period_short, _period_long, _period_id],
            'subject'    : [_subject_long, _subject_short, _subject_id],
            'assignment' : [_assignment_short, _assignment_long, _assignment_id],
            'delivery'   : [_delivery_time, _delivery_number, _delivery_success],
            }
        searchfields = [_subject_short,
                        _subject_long,
                        _period_short,
                        _period_long,
                        _assignment_long,
                        _assignment_short,
                        _delivery_success,
                        _delivery_number]
        methods = ['search', 'read']


@simplified_api
class Subject(PublishedWhereIsCandidateMixin):

    class Meta:

        _subject_long     = 'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'
        _subject_short    = 'delivery__assignment_group__parentnode__parentnode__parentnode__short_name'
        _subject_id       = 'delivery__assignment_group__parentnode__parentnode__parentnode__id'

        model = models.Subject
        resultfields = ['id', 'short_name', 'long_name', 'periods']
        searchfields = ['short_name', 'long_name', 'periods']
        methods = ['search', 'read']
