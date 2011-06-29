"""
.. attribute:: registry

    A :class:`Registry`-object.
"""


from django.conf import settings


class GradePluginDoesNotExistError(Exception):
    """ Raised when a grade plugin does not exist. """



def get_registry_key(model_cls):
    """ Get the registry key for the given model class. """
    meta = model_cls._meta
    return '%s:%s' % (meta.app_label, meta.module_name)


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

    def get_key(self):
        return get_registry_key(self.model_cls)

    def __str__(self):
        return self.label


class Registry(object):
    """
    Grade-plugin registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._registry = {}

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

    def getitem_from_cls(self, cls):
        """
        Get the :class:`RegistryItem` registered with the given class.
        """
        return self._registry[get_registry_key(cls)]

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the
        DEVILRY_DEFAULT_GRADEPLUGIN setting).
        """
        return settings.DEVILRY_DEFAULT_GRADEPLUGIN

    def iterlabels(self):
        """ Iterate over the registry yielding (key, label). """
        values = self._registry.values()
        values.sort(key=lambda i: i.label)
        for v in values:
            yield (v.get_key(), v)

    def iteritems(self):
        """ Iterate over the registry yielding (key, RegistryItem). """
        return self._registry.iteritems()

    def __iter__(self):
        return self.iterlabels()


registry = Registry()
