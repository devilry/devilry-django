import collections


class NoCrAdminInstanceFound(Exception):
    """
    Raised by :meth:`.CrAdminInstanceRegistry.get_current_instance`
    when no instance is found.
    """


class CrAdminInstanceRegistry:
    """
    We want the _current_ CrAdmin instance to be available
    without having to add it to all the views within the
    instance (we want to add it in a middleware and in a template context).

    At the same time, we want to be able to have multiple instances of CrAdmin
    running on the same site (imagine one site for employees and one for
    customers with a completely different look and feel).

    The solution is simple: If we have only a single instance, we do not
    need to do anything except adding it to this registry. If we have
    multiple instances, each of them must implement
    :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.matches_urlpath`.

    Example::

        from cradmin_legacy.crinstance import BaseCrAdminInstance
        from cradmin_legacy.registry import cradmin_instance_registry

        class MyCrAadminInstance(BaseCrAdminInstance):
            # ...

        cradmin_instance_registry.add(MyCrAadminInstance)
    """

    def __init__(self):
        self._registry = collections.OrderedDict()

    def get_instanceclass_by_id(self, id):
        """
        Get a CrAdmin instance class by ID (by :obj:`cradmin_legacy.crinstance.BaseCrAdminInstance.id`).
        """
        return self._registry[id]

    def get_instance_by_id(self, id, request):
        """
        Shortcut for ``get_instanceclass_by_id(id)(request)``.
        """
        return self.get_instanceclass_by_id(id)(request)

    def get_current_instance(self, request):
        """
        Get the current CrAdmin instance.

        Params:
            request (HttpRequest): The http request to the instance for.

        Returns:
            BaseCrAdminInstance: The CrAdmin instance for the given request.

        Raises:
            NoCrAdminInstanceFound: If no instance matching ``request.path`` is found.
        """
        if len(self._registry) == 1:
            return list(self._registry.values())[0](request)
        else:
            for instanceclass in list(self._registry.values()):
                if instanceclass.matches_urlpath(request.path):
                    return instanceclass(request)
            raise NoCrAdminInstanceFound(f"No CrAdminInstance matching {request.path} found")

    def add(self, cradmin_instance_class):
        """
        Add a CrAdmin instance to the registry.

        Parameters:
            cradmin_instance_class: A subclass of :class:`cradmin_legacy.crinstance.BaseCrAdminInstance`.
        """
        if cradmin_instance_class.id not in self._registry:
            self._registry[cradmin_instance_class.id] = cradmin_instance_class


cradmin_instance_registry = CrAdminInstanceRegistry()
