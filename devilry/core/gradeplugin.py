from django.conf import settings


class XmlrpcGradeConf(object):
    def __init__(self, help=None, isfile=False, filename=None):
        self.help = help
        self.isfile = isfile
        self.filename = filename


class RegistryItem(object):
    """ Information about a grade plugin.
    
    .. attribute:: model_cls::

        A class for storing grades.
    """
    def __init__(self, view, model_cls, label, description,
           admin_url_callback=None, xmlrpc_gradeconf=None):
        self.view = view
        self.xmlrpc_gradeconf = xmlrpc_gradeconf
        self.model_cls = model_cls
        self.label = label
        self.description = description
        self.admin_url_callback = admin_url_callback

    def get_key(self):
        meta = self.model_cls._meta
        return '%s:%s' % (meta.app_label, meta.module_name)

    def __str__(self):
        return self.label


class Registry(object):
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

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the
        DEVILRY_DEFAULT_GRADEPLUGIN setting.
        """
        return settings.DEVILRY_DEFAULT_GRADEPLUGIN

    def __iter__(self):
        values = self._registry.values()
        values.sort(key=lambda i: i.label)
        for v in values:
            yield (v.get_key(), v)


registry = Registry()
