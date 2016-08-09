from shutil import copy as shutil_copy
from os.path import join, exists
from os import makedirs, remove
from StringIO import StringIO
import posixpath

from importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage


def load_deliverystore_backend():
    s = settings.DEVILRY_DELIVERY_STORE_BACKEND.rsplit('.', 1)
    if len(s) != 2:
        raise ImproperlyConfigured(
            'Error splitting %s into module and classname.' %
            settings.DELIVERY_STORE)
    modulepath, classname = s
    try:
        module = import_module(modulepath)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing deliverystore backend %s: "%s"' % (
                modulepath, e))
    try:
        cls = getattr(module, classname)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" deliverystore backend' % (
                modulepath, classname))
    return cls()


class FileNotFoundError(Exception):
    """
    Exception to be raised when the remove method of a DeliveryStore
    does not find the given file.
    """
    def __init__(self, filemeta_obj):
        self.filemeta_obj = filemeta_obj

    def __str__(self):
        return "File not found: %s:%s" % (
                self.filemeta_obj.delivery,
                self.filemeta_obj.filename)


class MemFile(StringIO):
    def close(self):
        pass


class DeliveryStoreInterface(object):
    """
    The interface all deliverystores must implement. All methods raise
    ``NotImplementedError``.
    """

    # TODO: read_open when file does not exist?
    def read_open(self, filemeta_obj):
        """
        Return a file-like object opened for reading.
        
        The returned object must have ``close()`` and ``read()`` methods
        as defined by the documentation of the standard python file-class.

        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def write_open(self, filemeta_obj):
        """
        Return a file-like object opened for writing.
        
        The returned object must have ``close()`` and ``write()`` methods as
        defined by the documentation of the standard python file-class.

        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def remove(self, filemeta_obj):
        """
        Remove the file.

        Note that this method is called *before* the filemeta_obj is
        removed. This means that the file might be removed, and the removal
        of the filemeta_obj can still fail. To prevent users from having to
        manually resolve such cases implementations should check if the file
        exists, and raise FileNotFoundError if it does not.

        The calling function has to check for FileNotFoundError and
        handle any other error.

        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def exists(self, filemeta_obj):
        """
        Return ``True`` if the file exists, ``False`` if not.
        
        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def copy(self, filemeta_obj_from, filemeta_obj_to):
        """
        Copy the underlying file-object for ``filemeta_obj_from`` into the
        file-object for ``filemeta_obj_to``.

        Defaults to an inefficient implementation using :meth:`.read_open` and
        meth:`.write_open`. Should be overridden for backends with some form of
        native copy-capability.
        """
        infile = self.read_open(filemeta_obj_from)
        data = infile.read()
        infile.close()
        outfile = self.write_open(filemeta_obj_to)
        outfile.write(data)


class FsDeliveryStore(DeliveryStoreInterface):
    """
    Filesystem-based DeliveryStore suitable for production use.

    It stores files in a filesystem hierarcy with one directory for each
    Delivery, with the delivery-id as name. In each delivery-directory, the
    files are stored by FileMeta id.
    """
    def __init__(self, root=None):
        """
        :param root: The root-directory where files are stored. Defaults to the value of the ``DELIVERY_STORE_ROOT``-setting.
        """
        self.root = root or settings.DELIVERY_STORE_ROOT

    def _get_dirpath(self, delivery_obj):
        return join(self.root, str(delivery_obj.pk))

    def _get_filepath(self, filemeta_obj):
        return join(self._get_dirpath(filemeta_obj.delivery),
                    str(filemeta_obj.pk))

    def read_open(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        if not exists(filepath):
            raise FileNotFoundError(filemeta_obj)
        return open(filepath, 'rb')

    def _create_dir(self, filemeta_obj):
        dirpath = self._get_dirpath(filemeta_obj.delivery)
        if not exists(dirpath):
            makedirs(dirpath)

    def write_open(self, filemeta_obj):
        self._create_dir(filemeta_obj)
        return open(self._get_filepath(filemeta_obj), 'wb')

    def remove(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        if not exists(filepath):
            raise FileNotFoundError(filemeta_obj)
        remove(filepath)

    def exists(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        return exists(filepath)

    def copy(self, filemeta_obj_from, filemeta_obj_to):
        frompath = self._get_filepath(filemeta_obj_from)
        topath = self._get_filepath(filemeta_obj_to)
        self._create_dir(filemeta_obj_to)
        shutil_copy(frompath, topath)


class FsHierDeliveryStore(FsDeliveryStore):
    """
    Filesystem-based DeliveryStore suitable for production use with huge
    amounts of deliveries.
    """
    def __init__(self, root=None, interval=None):
        """
        :param root: The root-directory where files are stored. Defaults to
            the value of the ``DEVILRY_FSHIERDELIVERYSTORE_ROOT``-setting.
        :param interval: The interval. Defaults to
            the value of the ``DEVILRY_FSHIERDELIVERYSTORE_INTERVAL``-setting.
        """
        self.root = root or settings.DEVILRY_FSHIERDELIVERYSTORE_ROOT
        self.interval = interval or settings.DEVILRY_FSHIERDELIVERYSTORE_INTERVAL

    def get_path_from_deliveryid(self, deliveryid):
        """
        >>> fs = FsHierDeliveryStore('/stuff/', interval=1000)
        >>> fs.get_path_from_deliveryid(deliveryid=2001000)
        (2, 1)
        >>> fs.get_path_from_deliveryid(deliveryid=1000)
        (0, 1)
        >>> fs.get_path_from_deliveryid(deliveryid=1005)
        (0, 1)
        >>> fs.get_path_from_deliveryid(deliveryid=2005)
        (0, 2)
        >>> fs.get_path_from_deliveryid(deliveryid=0)
        (0, 0)
        >>> fs.get_path_from_deliveryid(deliveryid=1)
        (0, 0)
        >>> fs.get_path_from_deliveryid(deliveryid=1000000)
        (1, 0)
        """
        toplevel = deliveryid / (self.interval*self.interval)
        sublevel = (deliveryid - (toplevel*self.interval*self.interval)) / self.interval
        return toplevel, sublevel

    def _get_dirpath(self, delivery_obj):
        toplevel, sublevel = self.get_path_from_deliveryid(delivery_obj.pk)
        return join(self.root, str(toplevel), str(sublevel), str(delivery_obj.pk))


class MemoryDeliveryStore(DeliveryStoreInterface):
    """
    Memory-base DeliveryStore ONLY FOR TESTING.

    This is only for testing, and it does not handle parallel access.
    Suitable for unittesting.
    """
    def __init__(self):
        self.files = {}

    def read_open(self, filemeta_obj):
        try:
            f = self.files[filemeta_obj.id]
        except KeyError, e:
            raise FileNotFoundError(filemeta_obj)
        f.seek(0)
        return f

    def write_open(self, filemeta_obj):
        w = MemFile()
        self.files[filemeta_obj.id] = w
        return w

    def remove(self, filemeta_obj):
        if not filemeta_obj.id in self.files:
            raise FileNotFoundError(filemeta_obj)
        del self.files[filemeta_obj.id]

    def exists(self, filemeta_obj):
        return filemeta_obj.id in self.files


class DjangoStorageDeliveryStore(DeliveryStoreInterface):
    """
    Delivery store backend that uses Django storages.
    """
    def __init__(self, root=None, storage_backend=None):
        """
        Initialize the deliverystore with an optional root directory
        (relative to MEDIA_ROOT) and optionally a custom storage backend.

        Parameters:
            root: The root-directory relative to ``MEDIA_ROOT`` where files are stored.
                Defaults to the value of the ``DELIVERY_STORE_ROOT``-setting.
            storage_backend:
                The django storage backend to use.
                Defaults to ``django.core.files.storage.default_storage``.
        """
        self.root = root or settings.DELIVERY_STORE_ROOT
        if storage_backend:
            self.storage = storage_backend
        else:
            self.storage = default_storage

    def _get_filepath(self, filemeta_obj):
        return posixpath.join(self.root, str(filemeta_obj.pk))

    def read_open(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        if not self.storage.exists(filepath):
            raise FileNotFoundError(filemeta_obj)
        return self.storage.open(filepath, 'rb')

    def write_open(self, filemeta_obj):
        return self.storage.open(self._get_filepath(filemeta_obj), 'wb')

    def remove(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        if not self.storage.exists(filepath):
            raise FileNotFoundError(filemeta_obj)
        self.storage.delete(filepath)

    def exists(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        return self.storage.exists(filepath)

    def copy(self, filemeta_obj_from, filemeta_obj_to):
        frompath = self._get_filepath(filemeta_obj_from)
        topath = self._get_filepath(filemeta_obj_to)
        self.storage.save(topath, self.storage.open(frompath))


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
