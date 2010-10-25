"""
.. attribute:: registry

    A :class:`Registry`-object.
"""
from django.utils.translation import ugettext as _

class DashboardGroup(object):
    def __init__(self, title):
        self.title = title
        self.items = []
        self.group = None

    def additems(self, *items):
        for item in items:
            item.group = self
            self.items.append(item)

    def get_items(self, request):
        return [i for i in self.items if i.is_authorized(request)]


class DashboardItem(object):
    def __init__(self, title, url,
            check = lambda request: True):
        self.title = title
        self.url = url
        self.check = check

    def is_authorized(self, request):
        return self.check(request)


class DashboardView(object):
    def __init__(self, view, js=[]):
        self.view = view
        self.js = js


class DashboardRegistry(object):
    """
    Dashboard registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._groups = []
        self._views = []

    def create_group(self, *args, **kwargs):
        group = DashboardGroup(*args, **kwargs)
        self._groups.append(group)
        return group

    def add_view(self, view):
        self._views.append(view)

    def get_groups(self, request):
        groups = []
        for group in self._groups:
            items = group.get_items(request)
            if items:
                groups.append((group, items))
        return groups

    def get_views(self, request):
        items = []
        js_set = set()
        for item in self._views:
            for src in item.js:
                js_set.add(src)
            view = item.view
            items.append(view(request))
        return js_set, items



registry = DashboardRegistry()
personalgroup = registry.create_group(_('Personal'))
admingroup = registry.create_group(_('Administration'))
