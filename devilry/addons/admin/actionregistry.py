from devilry.ui.filtertable import RowAction


class RegistryRowAction(object):
    def __init__(self, label, urlcallback):
        self.label = label
        self.urlcallback = urlcallback

    def to_rowaction(self, rowdata):
        return RowAction(self.label, self.urlcallback(rowdata))

class RowActionRegistry(object):
    def __init__(self):
        self.actions = []

    def add_action(self, label, urlcallback):
        self.actions.append(RegistryRowAction(label, urlcallback))

    def as_list(self, rowdata):
        return [a.to_rowaction(rowdata) for a in self.actions]

period_rowactions = RowActionRegistry()
