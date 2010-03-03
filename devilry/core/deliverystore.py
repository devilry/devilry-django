from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from os.path import join, exists
from os import mkdir, listdir, remove
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

    def _get_filepath(self, filemeta_obj):
        return join(self._get_dirpath(filemeta_obj.delivery), str(filemeta_obj.pk))

    def read_open(self, filemeta_obj):
        return open(self._get_filepath(filemeta_obj), 'rb')

    def write_open(self, filemeta_obj):
        dirpath = self._get_dirpath(filemeta_obj.delivery)
        if not exists(dirpath):
            mkdir(dirpath)
        return open(self._get_filepath(filemeta_obj), 'wb')

    def remove(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        remove(fileath)
