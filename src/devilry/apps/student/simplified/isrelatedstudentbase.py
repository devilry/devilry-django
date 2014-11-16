from devilry.simplified import SimplifiedModelApi, PermissionDenied


class IsRelatedStudentBase(SimplifiedModelApi):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        """ Returns all objects of this type that matches arguments
        given in ``\*\*kwargs`` where ``user`` is a related student.

        :param user: A django user object.
        :param \*\*kwargs: A dict containing search-parameters.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_relatedstudent(user)

    @classmethod
    def read_authorize(cls, user, obj):
        """ Checks if the given ``user`` is an student in the given
        ``obj``, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: An object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not cls._meta.model.where_is_relatedstudent(user).filter(id=obj.id):
            raise PermissionDenied()
