

class GradePluginRegistry(object):
    """
    Global Registry Module for Valid Grade Plugins

    This registry holds information on each grade plugin the current setup uses.

    The registry is used for choice validation during Assignment/Grade setup
    and each new grade plugin must register itself.

    """
    def __init__(self):
        self.items = []

    def add(self, id, name):
        self.items.append((id, name))

    def __contains__(self, id):
        return id in self.items


gradeplugins = GradePluginRegistry()
