from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from os.path import join, exists
from os import mkdir
from StringIO import StringIO


def load_deliverystore_backend():
    s = settings.DELIVERY_STORE_BACKEND.rsplit('.', 1)
    if len(s) != 2:
        raise ImproperlyConfigured(
                'Error splitting %s into module and classname.' % settings.DELIVERY_STORE)
    modulepath, classname = s
    try:
        module = import_module(modulepath)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing deliverystore backend %s: "%s"' % (modulepath, e))
    try:
        cls = getattr(module, classname)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" deliverystore backend' % (modulepath, classname))
    return cls()


class FsDeliveryStore(object):
    def __init__(self):
        self.root = settings.DELIVERY_STORE_ROOT

    def _get_dirpath(self, delivery_obj):
        return join(self.root, str(delivery_obj.pk))

    def read_open(self, delivery_obj, filename):
        return open(join(self._get_dirpath(delivery_obj), filename), 'rb')

    def write_open(self, delivery_obj, filename):
        dirpath = self._get_dirpath(delivery_obj)
        if not exists(dirpath):
            mkdir(dirpath)
        return open(join(dirpath, filename), 'wb')


class MemoryDeliveryStore(object):
    def __init__(self):
        self._files = {}

    def _get_dir(self, delivery_obj):
        return self._files[delivery.pk]

    def read_open(self, delivery_obj, filename):
        return self._files[delivery.pk][filename]

    def write_open(self, delivery_obj, filename):
        if not delivery_obj.pk in self._files:
            self._files[delivery_obj.pk] = {}
        d = self._files[delivery_obj.pk][filename]
        d[filename] = StringIO()
        return d[filename]
