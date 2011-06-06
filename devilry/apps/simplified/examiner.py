from ..core import models
from can_save_authmixin import CanSaveAuthMixin
from simplified_api import simplified_api


class PublishedWhereIsExaminerMixin(object):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user)



@simplified_api
class Subject(CanSaveAuthMixin, PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Subject
        search_resultfields = ['id', 'short_name', 'long_name']
        search_searchfields = ['short_name', 'long_name']
        methods = ['search']


@simplified_api
class Period(CanSaveAuthMixin, PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Period
        search_resultfields = ['id', 'short_name', 'long_name', 'parentnode__short_name']
        search_searchfields = ['short_name', 'long_name', 'parentnode__short_name']
        methods = ['search']


@simplified_api
class Assignment(CanSaveAuthMixin):
    class Meta:
        model = models.Assignment
        search_resultfields = {
                    '__BASE__': ['id', 'short_name', 'long_name', 'parentnode__short_name'],
                    'long': ['parentnode__short_name', 'parentnode__long_name',
                        'parentnode__parentnode__long_name']}
        search_searchfields = ['short_name', 'long_name',
                'parentnode__short_name',
                'parentnode__parentnode__short_name']
        methods = ['search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        old = kwargs.pop('old', True)
        active = kwargs.pop('active', True)
        subject_short_name = kwargs.pop('subject_short_name', None)
        period_short_name = kwargs.pop('period_short_name', None)
        qryset = models.Assignment.published_where_is_examiner(user, old=old,
                active=active)
        if subject_short_name and period_short_name:
            qryset = qryset.filter(parentnode__short_name=period_short_name,
                    parentnode__parentnode__short_name=subject_short_name)
        return qryset


@simplified_api
class Group(CanSaveAuthMixin):
    class Meta:
        model = models.AssignmentGroup
        search_searchfields = ['name', 'candidates__student__username']
        search_resultfields = ['id', 'name']
        methods = ['search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        assignment = kwargs['assignment']
        return models.AssignmentGroup.published_where_is_examiner(user).filter(
                parentnode = assignment)
