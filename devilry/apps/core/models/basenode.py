from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from abstract_is_admin import AbstractIsAdmin
from save_interface import SaveInterface


class InheritedAdmin(object):
    """
    Stores reference to inherited admin, both to the
    :class:`django.contrib.auth.models.User` object, and to the
    :class:`.BaseNode` object.
    """
    def __init__(self, user, basenode):
        #: The :class:`django.contrib.auth.models.User`
        self.user = user

        #: The BaseNode
        self.basenode = basenode


class BaseNode(SaveInterface):
    """
    The base class of the Devilry hierarchy. Implements basic functionality
    used by the other Node classes. This is an abstract datamodel, so it
    is never used directly.


    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'.

    .. attribute:: long_name

        A django.db.models.CharField_ with max 100 characters. Gives a longer
        description than :attr:`short_name`.
    """

    def __unicode__(self):
        return self.get_path()

    def get_path(self):
        """ Get the unique path to this node.

        :return:
            A ``'.'`` separated list containing the short_name of this
            node and every parentnode required to make this path unique. For
            everything from Subject and down, this is up to subject, and for Node,
            this is up to a Node with ``parentnode==None``.
        """
        return self.parentnode.get_path() + "." + self.short_name
    get_path.short_description = _('Path')

    def get_admins(self):
        """ Get a string with the shortname of all administrators on this node
        separated by comma and a space like: ``"uioadmin, superuser"``.

        Note that admins on parentnode(s) is not included.
        """
        return u', '.join([u.shortname for u in self.admins.all()])
    get_admins.short_description = _('Administrators')

    def _get_inherited_admins(self, admins):
        for admin in self.admins.all():
            admins[admin.id] = InheritedAdmin(user=admin, basenode=self)
        if self.parentnode:
            self.parentnode._get_inherited_admins(admins)

    def get_inherited_admins(self):
        """
        Get list of inherited admins.

        :return:
            List of :class:`.InheritedAdmin` objects. Does
            not contain duplicates.
        """
        admins = {}
        if self.parentnode:
            self.parentnode._get_inherited_admins(admins)
        return admins.values()

    def get_all_admins(self):
        """
        Get all admins (including inherited) as a list of ``django.contrib.auth.model.User`` objects.
        """
        return set(list(self.get_inherited_admins()) + list(self.admins.all()))

    def get_all_admin_ids(self):
        """
        Get all admins (including inherited) as a set user-ids.
        """
        admin_ids = set([inheritedadmin.user.id for inheritedadmin in self.get_inherited_admins()])
        for user in self.admins.all():
            admin_ids.add(user.id)
        return admin_ids

    def is_admin(self, user_obj):
        """ Check if the given user is admin on this node or any parentnode.

        :param user_obj: A User object.
        :rtype: bool
        """
        try:
            self.admins.get(pk=user_obj.pk)
        except get_user_model().DoesNotExist:
            if self.parentnode:
                return self.parentnode.is_admin(user_obj)
        else:
            return True
        return False

    def _can_save_id_none(self, user_obj):
        """ Used by all except Node, which overrides. """
        return self.parentnode.is_admin(user_obj)

    def can_save(self, user_obj):
        """
        Check if the current user can save the current object. Unlike is_admin,
        this method returns true for superusers, and if this is a new object (id=None),
        we check if the user is admin on any parent.
        """
        if user_obj.is_superuser:
            return True
        if self.id is None:
            return self._can_save_id_none(user_obj)
        elif self.is_admin(user_obj):
            return True
        else:
            return False

    def is_empty(self):
        """
        Check if this node is empty (has no children). Used by
        :meth:`.can_delete` to determine if non-super-users are allowed to
        delete a node, but may also be useful in other situations.
        """
        raise NotImplementedError('is_empty must be implemented in subclasses.')

    def can_delete(self, user_obj):
        """
        Check if the given user is permitted to delete this object. A user is
        permitted to delete an object if the user is superadmin, or if the user
        is admin on the parentnode (uses :meth:`.is_admin`). Only superusers
        are allowed to delete nodes where :meth:`.is_empty` returns ``False``.

        :return: ``True`` if the user is permitted to delete this object.
        """
        if self.id is None:
            return False
        if user_obj.is_superuser:
            return True
        if self.parentnode is not None and self.is_empty():
            return self.parentnode.is_admin(user_obj)
        else:
            return False
