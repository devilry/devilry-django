from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied)
from devilry.coreutils.simplified.metabases import SimplifiedDeliveryMetaMixin


@simplified_modelapi
class SimplifiedDelivery(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedDeliveryMetaMixin):
        """ Defines what methods an Administrator can use on a Delivery object using the Simplified API """
        methods = ['search', 'read', 'create', 'update', 'delete']
        editablefields = ('successful', 'deadline', 'delivery_type', 'alias_delivery')

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is admin or superadmin.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def pre_full_clean(cls, user, obj):
        ExaminerSimplifiedDelivery.examiner_pre_full_clean(user, obj)

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
        ExaminerSimplifiedDelivery.write_authorize_examinercommon(user, obj)

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
