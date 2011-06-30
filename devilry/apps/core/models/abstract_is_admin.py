class AbstractIsAdmin(object):
    """ Abstract class implemented by all classes where it is natural to
    need to check if a user has admin rights. """

    @classmethod
    def q_is_admin(cls, user_obj):
        """
        Get a django.db.models.Q object matching all objects of this
        type where the given user is admin. The matched result is not
        guaranteed to contain unique items, so you should use distinct() on
        the queryset if this is required.

        This must be implemented in all subclassed.
        """
        raise NotImplementedError()

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Get all objects of this type where the given user is admin. """
        return cls.objects.filter(cls.q_is_admin(user_obj)).distinct()

    @classmethod
    def where_is_admin_or_superadmin(cls, user_obj):
        """ Get all objects of this type where the given user is admin, or
        all objects if the user is superadmin. """
        if user_obj.is_superuser:
            return cls.objects.all()
        else:
            return cls.where_is_admin(user_obj)
