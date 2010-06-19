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




class FileNotFoundError(Exception):
    """ Exception to be raised when the remove method of a DeliveryStore
    does not find the given file. """


class DeliveryStoreInterface(object):
    def read_open(self, filemeta_obj):
        """ Return a file-like object opened for reading.
        
        The returned object must at have close() and read() methods as
        defined by the documentation of the standard python file-class.
        """
        raise NotImplementedError()

    def write_open(self, filemeta_obj):
        """ Return a file-like object opened for writing.
        
        The returned object must at have close() and write() methods as
        defined by the documentation of the standard python file-class.
        """
        raise NotImplementedError()

    def remove(self, filemeta_obj):
        """ Remove the file.

        Note that this method is called *before* the filemeta_obj is
        removed. This means that the file might be removed, and the removal
        of the filemeta_obj can still fail. To prevent users from having to
        manually resolv such cases implementations should check if the file
        exists, and raise FileNotFoundError if it does not.

        The calling function has to check for FileNotFoundError and
        handle any other error.
        """
        raise NotImplementedError()


class FsDeliveryStore(DeliveryStoreInterface):
    def __init__(self, root=None):
        self.root = root or settings.DELIVERY_STORE_ROOT

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
        if not exists(filepath):
            raise FileNotFoundError('File not found: %s' % filepath)
        remove(filepath)


class MemoryDeliveryStore(DeliveryStoreInterface):
    """ Memory file storage ONLY FOR TESTING.

    This is only for testing, and it does not handle parallel access.
    """

    class MemFile(StringIO):
        def close(self):
            pass

    def __init__(self):
        self.files = {}

    def read_open(self, filemeta_obj):
        f = self.files[filemeta_obj.id]
        f.seek(0)
        return f

    def write_open(self, filemeta_obj):
        w = MemoryDeliveryStore.MemFile()
        self.files[filemeta_obj.id] = w
        return w

    def remove(self, filemeta_obj):
        if not  filemeta_obj.id in self.files:
            raise FileNotFoundError()
        del self.files[filemeta_obj.id]
