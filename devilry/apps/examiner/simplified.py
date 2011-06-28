from ...simplified import simplified_api, PermissionDenied, GetQryResult
from ..core import models


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
        resultfields = ['id', 'name'] #TODO add subject, period, assignment, candidates
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


@simplified_api
class Delivery(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Delivery
        resultfields = {
                    '__BASE__': ['time_of_delivery', 'number', 'delivered_by', 'id'],
                    'subject': ['assignment_group__parentnode__parentnode__parentnode__long_name',
                        'assignment_group__parentnode__parentnode__parentnode__short_name',
                        'assignment_group__parentnode__parentnode__parentnode__id'],
                    'period': [ 'assignment_group__parentnode__parentnode__long_name',
                        'assignment_group__parentnode__parentnode__short_name',
                        'assignment_group__parentnode__parentnode__id'],
                    'assignment':['assignment_group__parentnode__long_name', 
                        'assignment_group__parentnode__short_name',
                        'assignment_group__parentnode__id']
                    }
        searchfields = [
                #'delivered_by',
                'assignment_group__parentnode__short_name', # Name of assignment
                'assignment_group__parentnode__long_name', # Name of assignment
                'assignment_group__parentnode__parentnode__short_name', # Name of period
                'assignment_group__parentnode__parentnode__long_name', # Name of period
                'assignment_group__parentnode__parentnode__parentnode__short_name', # Name of subject
                'assignment_group__parentnode__parentnode__parentnode__long_name' # Name of subject
                ] # What should search() search from
        methods = ['search', 'read']



@simplified_api
class Feedback(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Feedback
        resultfields = {
                    '__BASE__': ['delivery', 'text', 'format', 'id'],
                    'subject': ['delivery__assignment_group__parentnode__parentnode__parentnode__long_name',
                        'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                        'delivery__assignment_group__parentnode__parentnode__parentnode__id'],
                    'period': [ 'delivery__assignment_group__parentnode__parentnode__long_name',
                        'delivery__assignment_group__parentnode__parentnode__short_name',
                        'delivery__assignment_group__parentnode__parentnode__id'],
                    'assignment':['delivery__assignment_group__parentnode__long_name', 
                        'delivery__assignment_group__parentnode__short_name',
                        'delivery__assignment_group__parentnode__id']
                    }
        searchfields = [
                #delivery__delivered_by
                'delivery__assignment_group__parentnode__parentnode__parentnode__long_name', #subject
                'delivery__assignment_group__parentnode__parentnode__parentnode__short_name', #subject
                'delivery__assignment_group__parentnode__parentnode__long_name', #period
                'delivery__assignment_group__parentnode__parentnode__short_name', #period
                'delivery__assignment_group__parentnode__long_name', #assignment
                'delivery__assignment_group__parentnode__short_name', #assignment
                ]
        methods = ['search', 'read', 'create'] #TODO 'delete', 'update'

