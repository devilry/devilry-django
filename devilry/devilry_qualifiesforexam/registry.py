from collections import OrderedDict


class RegistryItem(object):
    id = None

    def get_title(self):
        raise NotImplementedError()

    def get_description(self):
        raise NotImplementedError()

    def get_viewclass(self):
        raise NotImplementedError()

    def get_summary(self, status):
        """
        Generate a summary for the given ``status`` object with information about
        specific to this plugin.

        When porting the old plugins, this will be the same as the ``summarygenerator``.
        """
        raise NotImplementedError()


class Registry(object):
    def __init__(self):
        self.items = OrderedDict()

    def add(self, registryitem):
        self.items[registryitem.id] = registryitem

    def get(self, pluginid):
        return self.items[pluginid]

    def iterplugins(self):
        for pluginclass in self.items.values():
            plugin = pluginclass()
            yield plugin


qualifiesforexam_plugins = Registry()
