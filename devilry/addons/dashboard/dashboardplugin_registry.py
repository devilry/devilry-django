"""
.. attribute:: registry

    A :class:`Registry`-object.
"""

class DashboardItem(object):
    def __init__(self, title, view=None, candidate_access=False,
            examiner_access=False, admin_access=False, cssclass=''):
        self.title = title
        self.view = view
        self.candidate_access = candidate_access
        self.examiner_access = examiner_access
        self.admin_access = admin_access
    
    def can_show(self, is_candidate, is_examiner, is_admin):
        return (self.candidate_access and is_candidate) \
                or (self.examiner_access and is_examiner) \
                or (self.admin_access and is_admin)

    def getview(self, request, is_candidate, is_examiner, is_admin):
        return self.view(request, is_candidate, is_examiner, is_admin)


class DashboardRegistry(object):
    """
    Dashboard registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._important = []
        self._normal = []

    def register_important(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry with *important*
        priority.
        """
        self._important.append(registryitem)

    def register_normal(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry with *normal* priority.
        """
        self._normal.append(registryitem)

    def __getitem__(self, key):
        """
        Get the :class:`RegistryItem` registered with the given ``key``.
        """
        return self._registry[key]

    def _itervalues(self, request, lst, is_candidate=False, is_examiner=False,
            is_admin=False):
        for item in lst:
            if item.can_show(is_candidate, is_examiner, is_admin):
                view = item.getview(request, is_candidate, is_examiner,
                        is_admin)
                if view != None:
                    yield item, view

    def iterimportant(self, request, is_candidate=False, is_examiner=False,
                is_admin=False):
        return self._itervalues(request, self._important, is_candidate,
                is_examiner, is_admin)

    def iternormal(self, request, is_candidate=False, is_examiner=False,
                is_admin=False):
        return self._itervalues(request, self._normal, is_candidate,
                is_examiner, is_admin)


registry = DashboardRegistry()
