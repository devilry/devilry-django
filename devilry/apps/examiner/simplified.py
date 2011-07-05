from ...simplified import (simplified_modelapi, PermissionDenied,
                           QryResultWrapper, FieldSpec)
from ..core import models


class PublishedWhereIsExaminerMixin(object):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Subject
        resultfields = FieldSpec('id', 'short_name', 'long_name')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Period
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id',
                                 subject = ['parentnode__short_name', 'parentnode__long_name'])
        searchfields = FieldSpec('short_name', 'long_name', 'parentnode__short_name')
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Assignment
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id',
                                 period     = ['parentnode__short_name', 'parentnode__long_name',
                                           'parentnode__parentnode__id'],
                                 subject    = ['parentnode__parentnode__short_name',
                                            'parentnode__parentnode__long_name'])
        searchfields = FieldSpec('short_name', 'long_name',
                                 'parentnode__short_name',
                                 'parentnode__parentnode__short_name')
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


@simplified_modelapi
class SimplifiedAssignmentGroup(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.AssignmentGroup
        resultfields = FieldSpec('id', 'name',
                                assignment  = ['parentnode__short_name',
                                            'parentnode__long_name',
                                            'parentnode__id',],
                                period      = ['parentnode__parentnode__short_name',
                                            'parentnode__parentnode__long_name',
                                            'parentnode__parentnode__id'],
                                subject     = ['parentnode__parentnode__parentnode__long_name',
                                            'parentnode__parentnode__parentnode__short_name',
                                            'parentnode__parentnode__parentnode__id'])        
        searchfields = FieldSpec('name', 'candidates__candidate_id',
                                'parentnode__short_name', #assignment
                                'parentnode__long_name', #assignment
                                'parentnode__parentnode__short_name', #period
                                'parentnode__parentnode__long_name', #period
                                'parentnode__parentnode__parentnode__short_name', #subject 
                                'parentnode__parentnode__parentnode__long_name') #subject
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user, assignment, **kwargs):
        if isinstance(assignment, int):
            assignment = models.Assignment.objects.get(id=assignment)
        qryset = models.AssignmentGroup.published_where_is_examiner(user).filter(
                parentnode = assignment)
        fieldgroups = kwargs.pop('result_fieldgroups', None)
        resultfields = cls._meta.resultfields.aslist(fieldgroups)
        searchfields = cls._meta.searchfields.aslist(fieldgroups)
        if not assignment.anonymous:
            searchfields = list(searchfields)
            searchfields.append('candidates__student__username')
        result = QryResultWrapper(resultfields, searchfields, qryset)
        return result


@simplified_modelapi
class Delivery(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Delivery
        resultfields = FieldSpec('time_of_delivery', 'number', 'delivered_by', 'id',
                                 subject    = ['assignment_group__parentnode__parentnode__parentnode__long_name',
                                            'assignment_group__parentnode__parentnode__parentnode__short_name',
                                            'assignment_group__parentnode__parentnode__parentnode__id'],
                                 period     = ['assignment_group__parentnode__parentnode__long_name',
                                           'assignment_group__parentnode__parentnode__short_name',
                                           'assignment_group__parentnode__parentnode__id'],
                                 assignment =['assignment_group__parentnode__long_name', 
                                              'assignment_group__parentnode__short_name',
                                              'assignment_group__parentnode__id',
                                              "assignment_group__parentnode__anonymous"]
                                )
        searchfields = FieldSpec(
                                 #'delivered_by',
                                 'assignment_group__parentnode__short_name', # Name of assignment
                                 'assignment_group__parentnode__long_name', # Name of assignment
                                 'assignment_group__parentnode__parentnode__short_name', # Name of period
                                 'assignment_group__parentnode__parentnode__long_name', # Name of period
                                 'assignment_group__parentnode__parentnode__parentnode__short_name', # Name of subject
                                 'assignment_group__parentnode__parentnode__parentnode__long_name' # Name of subject
                                ) # What should search() search from
        methods = ['search', 'read']



@simplified_modelapi
class Feedback(PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.StaticFeedback
        resultfields = FieldSpec('delivery', 'text', 'format', 'id',
                                 subject    = ['delivery__assignment_group__parentnode__parentnode__parentnode__long_name',
                                            'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                                            'delivery__assignment_group__parentnode__parentnode__parentnode__id'],
                                 period     = ['delivery__assignment_group__parentnode__parentnode__long_name',
                                           'delivery__assignment_group__parentnode__parentnode__short_name',
                                           'delivery__assignment_group__parentnode__parentnode__id'],
                                 assignment = ['delivery__assignment_group__parentnode__long_name',
                                               'delivery__assignment_group__parentnode__short_name',
                                               'delivery__assignment_group__parentnode__id']
                                )
        searchfields = FieldSpec(
                                 #delivery__delivered_by
                                 'delivery__assignment_group__parentnode__parentnode__parentnode__long_name', #subject
                                 'delivery__assignment_group__parentnode__parentnode__parentnode__short_name', #subject
                                 'delivery__assignment_group__parentnode__parentnode__long_name', #period
                                 'delivery__assignment_group__parentnode__parentnode__short_name', #period
                                 'delivery__assignment_group__parentnode__long_name', #assignment
                                 'delivery__assignment_group__parentnode__short_name', #assignment
                                )
        methods = ['search', 'read', 'create'] #TODO 'delete', 'update'

