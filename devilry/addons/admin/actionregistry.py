from devilry.ui.filtertable import RowAction

# TODO: Change this so it uses ui.actionregistry


class RegistryAction(object):
    def __init__(self, label, urlcallback):
        self.label = label
        self.urlcallback = urlcallback

    def to_rowaction(self, rowdata):
        return RowAction(self.label, self.urlcallback(rowdata))

class ActionRegistry(object):
    def __init__(self):
        self.actions = []

    def add_action(self, label, urlcallback):
        self.actions.append(RegistryAction(label, urlcallback))

    def as_list(self, item):
        return [a.to_rowaction(item) for a in self.actions]


periodactions = ActionRegistry()
