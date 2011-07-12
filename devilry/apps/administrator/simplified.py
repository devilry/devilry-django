from ...simplified import (SimplifiedModelApi, simplified_modelapi,
                           PermissionDenied, FieldSpec,
                           FilterSpecs, FilterSpec, ForeignFilterSpec, PatternFilterSpec)
from ..core import models

from ..student.simplifiedmetabases import (SimplifiedNodeMetaMixin, SimplifiedSubjectMetaMixin,
                                           SimplifiedPeriodMetaMixin, SimplifiedAssignmentMetaMixin,
                                           SimplifiedAssignmentGroupMetaMixin, SimplifiedDeadlineMetaMixin,
                                           SimplifiedDeliveryMetaMixin, SimplifiedStaticFeedbackMetaMixin,
                                           SimplifiedFileMetaMetaMixin)

__all__ = ('SimplifiedNode', 'SimplifiedSubject', 'SimplifiedPeriod', 'SimplifiedAssignment')


class CanSaveBase(SimplifiedModelApi):
    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def read_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to ``obj``, and raise
        ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is admin or superadmin.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)


@simplified_modelapi
class SimplifiedNode(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta(SimplifiedNodeMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all node-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return models.Node.where_is_admin_or_superadmin(user)


@simplified_modelapi
class SimplifiedSubject(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(SimplifiedSubjectMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']


@simplified_modelapi
class SimplifiedPeriod(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(SimplifiedPeriodMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']


@simplified_modelapi
class SimplifiedAssignment(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(SimplifiedAssignmentMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']


@simplified_modelapi
class SimplifiedAssignmentGroup(CanSaveBase):
    """ Simplified wrapper for
    :class:`devilry.apps.core.models.AssignmentGroup`. """
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']


@simplified_modelapi
class SimplifiedDelivery(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all StaticFeedback-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an administrator for the given
        StaticFeedback ``obj`` or a superadmin, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A StaticFeedback object
        :throws PermissionDenied:
        """
        #TODO: Replace when issue #141 is resolved!
        if not user.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user):
                raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read', 'create', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all Deadline-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` is an administrator for the given
        Deadline ``obj`` or a superadmin, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.assignment_group.is_admin(user_obj):
                raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` can save changes to the
        AssignmentGroup of the given Deadline ``obj``, and raises
        ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        if not obj.assignment_group.can_save(user_obj):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.FileMeta`. """
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all FileMeta-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` is an administrator for the given
        FileMeta ``obj`` or a superadmin, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A FileMeta object.
        :throws PermissionDenied:
        """
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user_obj):
                raise PermissionDenied()
