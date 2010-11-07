
class RegistryAction(object):
    def __init__(self, label, urlcallback, tooltipcallback):
        self.label = label
        self.urlcallback = urlcallback
        self.tooltipcallback = tooltipcallback

    def getvalue(self, item):
        return dict(
            label = self.label,
            url = self.urlcallback(item),
            tooltip = self.tooltipcallback(item))

class ActionRegistry(object):
    """ Used when you need to plug actions to some item in an addon.

    A action is simply a label, a urlcallback and a optional tooltip.
    The url and tooltip are a callbacks because it takes the item send to
    :meth:`itervalues` as input, enabling other plugins to make urls and
    tooltips using the given item.
    """
    def __init__(self):
        self._actions = []

    def add_action(self, label, urlcallback, tooltipcallback=lambda i:i):
        """ Add a action to the registry. """
        self._actions.append(RegistryAction(label, urlcallback,
            tooltipcallback))

    def itervalues(self, item):
        """ Iterate over all values in the registry yielding a dictionary
        with label, url and label as keys. """
        for action in self._actions:
            yield action.getvalue(item)
