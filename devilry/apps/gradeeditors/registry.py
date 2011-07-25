"""
.. attribute:: gradeeditor_registry

    A :class:`Registry`-object.
"""


from django.conf import settings


class RegistryItem(object):
    """
    Information about a grade plugin.
    """
    def __init__(self, idstring, title, description):
        """
        All parameters are stored as object attributes.

        :param idstring:
            A unique string for this editor. If two editors with the same
            idstring is registered, an exception will be raised on load time.
        :param title:
            A short title for the grade editor.
        :param description:
            A longer description of the grade editor.
        """
        self.idstring = idstring
        self.title = title
        self.description = description

    def __str__(self):
        return self.title


class Registry(object):
    """
    Grade-plugin registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._registry = {'approved': RegistryItem('approved', 'Fake', 'Fake')} # TODO: This hack must be replaced when we develop the new grade plugins

    def register(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry.
        """
        if registryitem.idstring in self._registry:
            raise ValueError('More than one gradeeditor with idstring: {0}'.format(registryitem.idstring))
        self._registry[registryitem.idstring] = registryitem

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the DEVILRY_DEFAULT_GRADEEDITOR setting).
        """
        return settings.DEVILRY_DEFAULT_GRADEEDITOR

    def itertitles(self):
        """ Iterate over the registry yielding (key, title). """
        for key, item in self._registry.iteritems():
            yield key, item.title


gradeeditor_registry = Registry()
