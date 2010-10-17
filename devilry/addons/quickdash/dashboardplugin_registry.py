"""
.. attribute:: registry

    A :class:`Registry`-object.
"""
from itertools import chain

class DashboardItem(object):
    def __init__(self, title, view=None, candidate_access=False,
            examiner_access=False, nodeadmin_access=False,
            subjectadmin_access=False, periodadmin_access=False,
            assignmentadmin_access=False, cssclass='',
            js=[]):
        self.title = title
        self.view = view
        self.candidate_access = candidate_access
        self.examiner_access = examiner_access
        self.nodeadmin_access = nodeadmin_access
        self.subjectadmin_access = subjectadmin_access
        self.periodadmin_access = periodadmin_access
        self.assignmentadmin_access = assignmentadmin_access
        self.js = js
    
    def can_show(self, is_candidate, is_examiner, is_nodeadmin,
            is_subjectadmin, is_periodadmin, is_assignmentadmin):
        return (self.candidate_access and is_candidate) \
                or (self.examiner_access and is_examiner) \
                or (self.nodeadmin_access and is_nodeadmin) \
                or (self.subjectadmin_access and is_subjectadmin) \
                or (self.periodadmin_access and is_periodadmin) \
                or (self.assignmentadmin_access and is_assignmentadmin)

    def getview(self, request, *args, **kw):
        return self.view(request, *args, **kw)


class DashboardRegistry(object):
    """
    Dashboard registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._important = []
        self._normal = []
        self._js = set()

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

    def iterjs(self, is_candidate=False, is_examiner=False,
            is_nodeadmin=False, is_subjectadmin=False, is_periodadmin=False,
            is_assignmentadmin=False):
        s = set()
        for item in chain(self._important, self._normal):
            if item.can_show(is_candidate, is_examiner, is_nodeadmin,
                    is_subjectadmin, is_periodadmin, is_assignmentadmin):
                s.update(item.js)
        return s.__iter__()

    def _itervalues(self, request, lst, is_candidate=False, is_examiner=False,
            is_nodeadmin=False, is_subjectadmin=False, is_periodadmin=False,
            is_assignmentadmin=False):
        for item in lst:
            if item.can_show(is_candidate, is_examiner, is_nodeadmin,
                    is_subjectadmin, is_periodadmin, is_assignmentadmin):
                view = item.getview(request, is_candidate, is_examiner,
                        is_nodeadmin, is_subjectadmin, is_periodadmin,
                        is_assignmentadmin)
                if view != None:
                    yield item, view

    def iterimportant(self, request, *args, **kw):
        return self._itervalues(request, self._important, *args, **kw)

    def iternormal(self, request, *args, **kw):
        return self._itervalues(request, self._normal, *args, **kw)


registry = DashboardRegistry()
