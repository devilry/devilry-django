from django.db.models import Count

from ...simplified import SimplifiedModelApi, simplified_modelapi, PermissionDenied, FieldSpec
from ..core import models
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedFileMetaMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,)



class PublishedWhereIsExaminerMixin(SimplifiedModelApi):
    """ Mixin class extended by many of the classes in the Simplified API for Examiner """

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is an examiner.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.published_where_is_examiner(user)

    @classmethod
    def read_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an examiner for the given 
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not cls._meta.model.published_where_is_examiner(user).filter(id=obj.id):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedSubject(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(SimplifiedSubjectMetaMixin):
        """ Defines what methods an Examiner can use on a Subject object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        """ Defines what methods an Examiner can use on a Period object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
        """ Defines what methods an Examiner can use on an Assignment object using the Simplified API """
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all Assignment objects that matches the arguments
        given in ``\*\*kwargs`` where ``user`` is an examiner.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
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
    """ Simplified wrapper for :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        """ Defines what methods an Examiner can use on an AssignmentGroup object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods an Examiner can use on a Delivery object using the Simplified API """
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.StaticFeedback`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        """ Defines what methods an Examiner can use on a StaticFeedback
        object using the Simplified API. Also adds to the resultfields
        returned by search """
        methods = ['search', 'read', 'create']
        # Examiners need a few more fields than is given by
        # default in SimplifiedStaticFeedbackMetaMixin. Addition them in!
        resultfields = SimplifiedStaticFeedbackMetaMixin.resultfields + FieldSpec('points')
        editablefields = ['grade', 'is_passing_grade', 'points',
                          'rendered_view', 'delivery']

    @classmethod
    def pre_full_clean(cls, user, obj):
        if not obj.id == None:
            raise ValueError('BUG: Examiners should only have create permission on StaticFeedback.')
        obj.saved_by = user

    @classmethod
    def write_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an examiner in the given
        StaticFeedback ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A StaticFeedback-object.
        :throws PermissionDenied:
        """
        if not obj.delivery.deadline.assignment_group.is_examiner(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        """ Defines what methods an Examiner can use on a Deadline object using the Simplified API """
        methods = ['search', 'read', 'create', 'delete']  # TODO: should we have update here?

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user).annotate(number_of_deliveries=Count('deliveries'))

    @classmethod
    def write_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an examiner in the given
        Deadline ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline-object.
        :throws PermissionDenied:
        """
        if not obj.assignment_group.is_examiner(user):
            raise PermissionDenied()

    @classmethod
    def is_empty(cls, obj):
        return obj.deliveries.count() == 0

@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        """ Defines what methods an Examiner can use on a FileMeta object using the Simplified API """
        methods = ['search', 'read']
