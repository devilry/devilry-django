from ..core import models
from simplified_api import simplified_api
from exceptions import PermissionDenied
from getqryresult import GetQryResult


class PublishedWhereIsExaminerMixin(object):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_api
class Subject(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Subject
        resultfields = ['id', 'short_name', 'long_name']
        searchfields = ['short_name', 'long_name']
        methods = ['search', 'read']


@simplified_api
class Period(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Period
        resultfields = {
                '__BASE__': ['id', 'short_name', 'long_name', 'parentnode__id'],
                'subject': ['parentnode__short_name', 'parentnode__long_name']}
        searchfields = ['short_name', 'long_name', 'parentnode__short_name']
        methods = ['search', 'read']


@simplified_api
class Assignment(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Assignment
        resultfields = {
                    '__BASE__': ['id', 'short_name', 'long_name', 'parentnode__id'],
                    'period': ['parentnode__short_name', 'parentnode__long_name',
                        'parentnode__parentnode__id'],
                    'subject': ['parentnode__parentnode__short_name',
                        'parentnode__parentnode__long_name']}
        searchfields = ['short_name', 'long_name',
                'parentnode__short_name',
                'parentnode__parentnode__short_name']
        methods = ['search', 'read']

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
class AssignmentGroup(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.AssignmentGroup
        resultfields = ['id', 'name']
        searchfields = ['name', 'candidates__candidate_id']
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user, assignment, **kwargs):
        if isinstance(assignment, int):
            assignment = models.Assignment.objects.get(id=assignment)
        qryset = models.AssignmentGroup.published_where_is_examiner(user).filter(
                parentnode = assignment)
        if assignment.anonymous:
            searchfields = cls._meta.searchfields
        else:
            searchfields = list(cls._meta.searchfields) # Important to copy this! If we do not, we append to the class variable.
            searchfields.append('candidates__student__username')
        result = GetQryResult(cls._meta.resultfields, searchfields, qryset)
        return result
