
class RegistryAction(object):
    def __init__(self, labelcallback, urlcallback, tooltipcallback):
        self.labelcallback = labelcallback
        self.urlcallback = urlcallback
        self.tooltipcallback = tooltipcallback

    def getvalue(self, item):
        return dict(
            label = self.labelcallback(item),
            url = self.urlcallback(item),
            tooltip = self.tooltipcallback(item))

class ActionRegistry(object):
    """ Used when you need to plug actions to some item in an addon.

    A action is simply a label-callback, a urlcallback and a optional
    tooltip-callback.

    They are callbacks to enable them to use the item sent to
    :meth:`itervalues`.
    """
    def __init__(self):
        self._actions = []

    def add_action(self, labelcallback, urlcallback,
            tooltipcallback=lambda i:i):
        """ Add a action to the registry. """
        self._actions.append(RegistryAction(labelcallback, urlcallback,
            tooltipcallback))

    def itervalues(self, item):
        """ Iterate over all values in the registry yielding a dictionary
        with label, url and label as keys. """
        for action in self._actions:
            yield action.getvalue(item)
