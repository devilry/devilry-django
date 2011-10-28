from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied)
from devilry.coreutils.simplified.metabases import SimplifiedStaticFeedbackMetaMixin


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Delivery`. """
    class Meta(SimplifiedStaticFeedbackMetaMixin):
        """ Defines what methods an Administrator can use on a StaticFeedback object using the Simplified API """
        methods = ['search', 'read', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all StaticFeedback-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.delivery.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
