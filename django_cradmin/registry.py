from builtins import object
import collections


class CrAdminInstanceRegistry(object):
    def __init__(self):
        self._registry = collections.OrderedDict()

    def get_instanceclass_by_id(self, id):
        """
        Get a CrAdmin instance class by ID (by :obj:`django_cradmin.crinstance.BaseCrAdminInstance.id`).
        """
        return self._registry[id]

    def get_instance_by_id(self, id, request):
        """
        Shortcut for ``get_instanceclass_by_id(id)(request)``.
        """
        return self.get_instanceclass_by_id(id)(request)

    def add(self, cradmin_instance_class):
        """
        Add a CrAdmin instance to the registry.

        Parameters:
            cradmin_instance_class: A subclass of :class:`django_cradmin.crinstance.BaseCrAdminInstance`.
        """
        if cradmin_instance_class.id not in self._registry:
            self._registry[cradmin_instance_class.id] = cradmin_instance_class


cradmin_instance_registry = CrAdminInstanceRegistry()
