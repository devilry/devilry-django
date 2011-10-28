from devilry.simplified import (SimplifiedModelApi, PermissionDenied)


class CanSaveBase(SimplifiedModelApi):
    """ Mixin class extended by many of the classes in the Simplified API for Administrator """
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
