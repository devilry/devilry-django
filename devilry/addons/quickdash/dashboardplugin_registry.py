"""
.. attribute:: registry

    A :class:`Registry`-object.
"""

class DashboardGroup(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.items = []

    def additems(self, *items):
        self.items += items

    def parseitems(self, request, js_set):
        items = []
        for item in self.items:
            view = item.getview(request)
            if view != None:
                js = []
                if item.js:
                    for src in item.js:
                        if not src in js_set:
                            js.append(src)
                            js_set.add(src)
                items.append((item, js, view))
        return items


class DashboardItem(object):
    def __init__(self, id, title, view=None, js=[]):
        self.title = title
        self.id = id
        self.view = view
        self.js = js

    def getview(self, request, *args, **kw):
        return self.view(request, *args, **kw)


class DashboardRegistry(object):
    """
    Dashboard registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._groups = []

    def create_group(self, *args, **kwargs):
        group = DashboardGroup(*args, **kwargs)
        self._groups.append(group)
        return group

    def parsegroups(self, request):
        js_set = set()
        groups = []
        for group in self._groups:
            groups.append((group, group.parseitems(request, js_set)))
        return groups



registry = DashboardRegistry()
