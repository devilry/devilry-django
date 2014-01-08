class GradePluginItem(object):
    """
    Interface for new grade plugins. Makes the grade plugin ready for the global register

    This interface must be implemented by each grade plugin in the running system.
    this holds all the global information necessary to be able to
    manage the grade plugin layout and to cover smooth transition between different
    grade plugins on different Assignments

    """
    requires_configuration = False

    @staticmethod
    def get_configuration_url(assignment):
        raise NotImplementedError("Needed for registry")

    @staticmethod
    def get_edit_feedback_url(assignment):
        raise NotImplementedError("Needed for registry")

    @staticmethod
    def is_configured(assignment):
        raise NotImplementedError("Needed for registry")


class GradePluginRegistry(object):
    """
    Global Registry Module for Valid Grade Plugins

    This registry holds information on each grade plugin the current setup uses.

    The registry is used for choice validation during Assignment/Grade setup
    and each new grade plugin must register itself.

    """
    def __init__(self):
        self.items = {}

    def add(self, registryitem):
        self.items[registryitem.id] = registryitem

    def __contains__(self, id):
        return id in self.items


gradeplugins = GradePluginRegistry()
