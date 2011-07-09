"""
.. attribute:: registry

    A :class:`Registry`-object.
"""


from django.conf import settings


class GradePluginDoesNotExistError(Exception):
    """ Raised when a grade plugin does not exist. """



class RegistryItem(object):
    """
    Information about a grade plugin.
    """
    def __init__(self, view, label, description):
        """
        All parameters are stored as object attributes.

        :param view:
            The view used when creating/editing feedback with this grade-plugin.
        :param model_cls:
            A class for storing the grade of a single Feedback. It us used in a
            one-to-one relationship with :class:`devilry.core.models.Feedback`
            (The Feedback-class takes care of the relationship).
        """
        self.view = view
        self.label = label
        self.description = description

    def __str__(self):
        return self.label


class Registry(object):
    """
    Grade-plugin registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._registry = {'fake': RegistryItem(None, 'fake', 'Fake')} # TODO: This hack must be replaced when we develop the new grade plugins

    def register(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry.
        """
        self._registry[registryitem.get_key()] = registryitem

    def getitem(self, key):
        """
        Get the :class:`RegistryItem` registered with the given ``key``.
        """
        return self._registry[key]

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the
        DEVILRY_DEFAULT_GRADEPLUGIN setting).
        """
        return settings.DEVILRY_DEFAULT_GRADEPLUGIN

    def iterlabels(self):
        """ Iterate over the registry yielding (key, label). """
        for key, item in self._registry.iteritems():
            yield key, item.label

    def iteritems(self):
        """ Iterate over the registry yielding (key, RegistryItem). """
        return self._registry.iteritems()

    def __iter__(self):
        return self.iterlabels()


registry = Registry()
