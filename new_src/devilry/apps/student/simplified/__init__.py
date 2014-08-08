from datetime import datetime
from django.db.models import Count, Max
import django.dispatch
from django.db.models import Q

from devilry.simplified import simplified_modelapi, SimplifiedModelApi, PermissionDenied, FieldSpec
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin)
from devilry.apps.core.models import AssignmentGroup, Delivery
from isrelatedstudentbase import IsRelatedStudentBase
from simplifiedrelatedstudentkeyvalue import SimplifiedRelatedStudentKeyValue


successful_delivery_signal = django.dispatch.Signal(providing_args=["delivery"])


class PublishedWhereIsCandidateMixin(SimplifiedModelApi):
    """ Mixin class extended by all classes in the Simplified API for Student using the Simplified API """

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is a student.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.published_where_is_candidate(user)

    @classmethod
    def read_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an student in the given
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not cls._meta.model.published_where_is_candidate(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        """ Defines what methods a Student can use on a FileMeta object using the Simplified API """
        methods = ['search', 'read', 'create']


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        """ Defines what methods a Student can use on a Deadline object using the Simplified API """
        methods = ['search', 'read']
        editablefields = tuple()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_candidate(user).annotate(number_of_deliveries=Count('deliveries'))


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.StaticFeedback`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        """ Defines what methods a Student can use on a StaticFeedback object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods a Student can use on a Delivery object using the Simplified API """
        methods = ['search', 'read', 'create', 'update']
        editablefields = ('successful', 'deadline')

    @classmethod
    def pre_full_clean(cls, user, obj):
        obj.time_of_delivery = datetime.now()
        candidate = obj.deadline.assignment_group.candidates.get(student=user)
        obj.delivered_by = candidate
        if obj.id == None:
            obj.number = 0

    @classmethod
    def write_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an student in the given
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not AssignmentGroup.published_where_is_candidate(user).filter(id=obj.deadline.assignment_group.id):
            raise PermissionDenied()
        if obj.id != None:
            current = Delivery.objects.get(id=obj.id)
            if current.successful:
                raise PermissionDenied()

    @classmethod
    def post_save(cls, user, delivery):
        if delivery.successful:
            successful_delivery_signal.send_robust(sender=delivery, delivery=delivery)


@simplified_modelapi
class SimplifiedAssignmentGroup(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        """ Defines what methods a Student can use on an AssignmentGroup object using the Simplified API """
        methods = ['search', 'read']

        # TODO: Replace all uses of candidates__student__username with candidates in SimplifiedAssignmentGroupMetaMixin
        resultfields = FieldSpec(users=['candidates__identifier']) +SimplifiedAssignmentGroupMetaMixin.resultfields

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all AssignmentGroup-objects where given ``user`` is candidate.

        :param user: A django user object.
        :rtype: a django queryset
        """
        qry = cls._meta.model.published_where_is_candidate(user)
        qry = qry.annotate(latest_delivery_id=Max('deadlines__deliveries__id'),
                           latest_deadline_id=Max('deadlines__id'),
                           latest_deadline_deadline=Max('deadlines__deadline'),
                           number_of_deliveries=Count('deadlines__deliveries'))
        qry = qry.filter(Q(Q(latest_deadline_deadline__gte=datetime.now()) & Q(parentnode__deadline_handling__exact=1)) |
                         Q(parentnode__deadline_handling__exact=0))
        return qry



@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
        """ Defines what methods a Student can use on an Assignment object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(IsRelatedStudentBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        """ Defines what methods a Student can use on a Period object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsCandidateMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(SimplifiedSubjectMetaMixin):
        """ Defines what methods a Student can use on a Subject object using the Simplified API """
        methods = ['search', 'read']
