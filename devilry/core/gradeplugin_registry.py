_registry = {}

def register(view, model_cls, label, description,
        admin_url_callback=None, xmlrpc_conf=None):
    r = RegistryItem(view, model_cls, label, description,
            admin_url_callback, xmlrpc_conf)
    _registry[r.get_key()] = r

def get(key):
    return _registry[key]


class RegistryItem(object):
    """ Information about a grade plugin.
    
    .. attribute:: model_cls::

        A class for storing grades.
    """
    def __init__(self, view, model_cls, label, description,
            admin_url_callback, xmlrpc_conf=None):
        self.view = view
        self.xmlrpc_conf = xmlrpc_conf
        self.model_cls = model_cls
        self.label = label
        self.description = description
        self.admin_url_callback = admin_url_callback

    def get_key(self):
        meta = self.model_cls._meta
        return '%s:%s' % (meta.app_label, meta.module_name)

    def __unicode__(self):
        return self.label


class KeyLabelIterable(object):
    """ Iterator over the gradeplugin-registry yielding (key, RegistryItem).
    The iterator is sorted by :attr:`RegistryItem.label`. """
    def __iter__(self):
        values = _registry.values()
        values.sort(key=lambda i: i.label)
        for v in values:
            yield (v.get_key(), v)
