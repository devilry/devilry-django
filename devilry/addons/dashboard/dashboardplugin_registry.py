class RegistryItem(object):
    def __init__(self, key, label, url, icon, description):
        self.key = key
        self.label = label
        self.url = url
        self.icon = icon
        self.description = description

    def get_key(self):
        return '%s' % (key)

_registry = {}

def register(key, label, url, icon, description, *arguments, **keywords):
    r = RegistryItem(key, label, url, icon, description)
    print r.get_key()
    print "%s %s %s %s %s" % (key, label, url, icon, description)
    _registry[r.get_key()] = r

def get(key):
    return _registry[key]

def values():
    return _registry.values()

class KeyLabelIterable(object):
    def __iter__(self):
        keys = _registry.keys()
        keys.sort()
        for key in keys:
            yield (key, _registry[key].description)
