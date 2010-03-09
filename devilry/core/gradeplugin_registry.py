class RegistryItem(object):
    def __init__(self, view, model_cls, description):
        self.view = view
        self.model_cls = model_cls
        self.description = description

    def get_key(self):
        meta = self.model_cls._meta
        return '%s:%s' % (meta.app_label, meta.module_name)

_registry = {}
def register(view, model_cls, description):
    r = RegistryItem(view, model_cls, description)
    print r.get_key()
    _registry[r.get_key()] = r

def get(key):
    return _registry[key]

class KeyLabelIterable(object):
    def __iter__(self):
        keys = _registry.keys()
        keys.sort()
        for key in keys:
            yield (key, _registry[key].description)
