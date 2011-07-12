from ...simplified import SimplifiedModelApi, simplified_modelapi, PermissionDenied, FieldSpec
from ..core import models
from ..student.simplifiedmetabases import (SimplifiedSubjectMetaMixin, SimplifiedFileMetaMetaMixin,
                                           SimplifiedPeriodMetaMixin, SimplifiedAssignmentMetaMixin,
                                           SimplifiedAssignmentGroupMetaMixin, SimplifiedDeadlineMetaMixin,
                                           SimplifiedDeliveryMetaMixin, SimplifiedStaticFeedbackMetaMixin,)


class PublishedWhereIsExaminerMixin(SimplifiedModelApi):
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
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedPeriod(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedAssignment(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
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
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedDelivery(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.StaticFeedback`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read', 'create']
        # Examiners need a few more fields than is given by
        # default in SimplifiedStaticFeedbackMetaMixin. Addition them in!
        resultfields = SimplifiedStaticFeedbackMetaMixin.resultfields + FieldSpec('points')

    @classmethod
    def write_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an examiner in the given
        StaticFeedback ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A StaticFeedback-object.
        :throws PermissionDenied:
        """
        if not obj.delivery.assignment_group.is_examiner(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read', 'create', 'delete']  # TODO: should we have update here?

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


@simplified_modelapi
class SimplifiedFileMeta(PublishedWhereIsExaminerMixin):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read']
