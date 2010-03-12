class RegistryItem(object):
    def __init__(self, view, model_cls, label, description, admin_url_callback):
        self.view = view
        self.model_cls = model_cls
        self.label = label
        self.description = description
        self.admin_url_callback = admin_url_callback

    def get_key(self):
        meta = self.model_cls._meta
        return '%s:%s' % (meta.app_label, meta.module_name)

_registry = {}
def register(view, model_cls, label, description, admin_url_callback=None):
    r = RegistryItem(view, model_cls, label, description, admin_url_callback)
    _registry[r.get_key()] = r

def get(key):
    return _registry.get(key)

class KeyLabelIterable(object):
    def __iter__(self):
        keys = _registry.keys()
        keys.sort()
        for key in keys:
            yield (key, _registry[key].label)
