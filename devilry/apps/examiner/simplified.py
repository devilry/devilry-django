from ...simplified import SimplifiedModelApi, simplified_modelapi, PermissionDenied, FieldSpec
from ..core import models
from ..student.simplifiedmetabases import (SimplifiedSubjectMetaMixin, SimplifiedFileMetaMetaMixin,
                                           SimplifiedPeriodMetaMixin, SimplifiedAssignmentMetaMixin,
                                           SimplifiedAssignmentGroupMetaMixin, SimplifiedDeadlineMetaMixin,
                                           SimplifiedDeliveryMetaMixin, SimplifiedStaticFeedbackMetaMixin,)


class PublishedWhereIsExaminerMixin(SimplifiedModelApi):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedSubjectMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedPeriodMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedAssignmentMetaMixin):
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
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read', 'create']
        # Examiners need a few more fields than is given by
        # default in SimplifiedStaticFeedbackMetaMixin. Addition them in!
        resultfields = SimplifiedStaticFeedbackMetaMixin.resultfields + FieldSpec('points')

    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.delivery.assignment_group.is_examiner(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read', 'create', 'delete']  # TODO: should we have update here?

    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.assignment_group.is_examiner(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsExaminerMixin):
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read']
