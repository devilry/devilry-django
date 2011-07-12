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
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.where_is_admin_or_superadmin(user)


@simplified_modelapi
class SimplifiedNode(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta(SimplifiedNodeMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user):
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
    class Meta(SimplifiedAssignmentGroupMetaMixin):
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']


@simplified_modelapi
class SimplifiedDelivery(CanSaveBase):
    class Meta(SimplifiedDeliveryMetaMixin):
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi):
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user):
                raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(SimplifiedModelApi):
    class Meta(SimplifiedDeadlineMetaMixin):
        methods = ['search', 'read', 'create', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.assignment_group.is_admin(user_obj):
                raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user_obj, obj):
        if not obj.assignment_group.can_save(user_obj):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(SimplifiedModelApi):
    class Meta(SimplifiedFileMetaMetaMixin):
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user_obj):
                raise PermissionDenied()
