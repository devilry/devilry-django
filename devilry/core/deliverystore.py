from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from os.path import join, exists
from os import mkdir, remove
from StringIO import StringIO
import dumbdbm


def load_deliverystore_backend():
    s = settings.DELIVERY_STORE_BACKEND.rsplit('.', 1)
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
    """ Exception to be raised when the remove method of a DeliveryStore
    does not find the given file. """
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
    """ The interface all deliverystores must implement. All methods raise
    ``NotImplementedError``. """

    # TODO: read_open when file does not exist?
    def read_open(self, filemeta_obj):
        """ Return a file-like object opened for reading.
        
        The returned object must have ``close()`` and ``read()`` methods
        as defined by the documentation of the standard python file-class.

        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def write_open(self, filemeta_obj):
        """ Return a file-like object opened for writing.
        
        The returned object must have ``close()`` and ``write()`` methods as
        defined by the documentation of the standard python file-class.

        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()

    def remove(self, filemeta_obj):
        """ Remove the file.

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
        """ Return ``True`` if the file exists, ``False`` if not.
        
        :param filemeta_obj: A :class:`devilry.core.models.FileMeta`-object.
        """
        raise NotImplementedError()


class FsDeliveryStore(DeliveryStoreInterface):
    """ Filesystem-based DeliveryStore suitable for production use.

    It stores files in a filesystem hierarcy with one directory for each
    Delivery, with the delivery-id as name. In each delivery-directory, the
    files are stored by FileMeta id.
    """
    def __init__(self, root=None):
        """
        :param root: The root-directory where files are stored. Defaults to
            the value of the ``DELIVERY_STORE_ROOT``-setting.
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

    def write_open(self, filemeta_obj):
        dirpath = self._get_dirpath(filemeta_obj.delivery)
        if not exists(dirpath):
            mkdir(dirpath)
        return open(self._get_filepath(filemeta_obj), 'wb')

    def remove(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        if not exists(filepath):
            raise FileNotFoundError(filemeta_obj)
        remove(filepath)

    def exists(self, filemeta_obj):
        filepath = self._get_filepath(filemeta_obj)
        return exists(filepath)


class DbmDeliveryStore(DeliveryStoreInterface):
    """Dbm DeliveryStore ONLY FOR TESTING."""

    class FileWriter(object):
        def __init__(self, dbm, key):
            self.dbm = dbm
            self.key = key
            self.data = StringIO()

        def write(self, s):
            self.data.write(s)

        def close(self):
            self.dbm[self.key] = self.data.getvalue()
            self.dbm.close()

    def __init__(self, filename=None, dbm=dumbdbm):
        """
        :param filename:
            The dbm-file where files are stored. Defaults to
            the value of the ``DELIVERY_STORE_DBM_FILENAME``-setting.
        :param dbm:
            The dbm implementation. This defaults to :mod:`dumbdbm` for
            portability of the data-files because this DeliveryStore is
            primarly for development and database storage in the devilry
            git-repo. But the parameter is provided to make it really easy
            to create a DeliveryStore using a more efficient dbm, like gdbm.
        """
        self.dbm = dbm
        self.filename = filename or settings.DELIVERY_STORE_DBM_FILENAME

    def _get_key(self, filemeta_obj):
        return str(filemeta_obj.pk)

    def read_open(self, filemeta_obj):
        try:
            data = self.dbm.open(self.filename, 'r')[self._get_key(filemeta_obj)]
        except KeyError, e:
            raise FileNotFoundError(filemeta_obj)
        return MemFile(data)

    def write_open(self, filemeta_obj):
        dbm = self.dbm.open(self.filename, 'c')
        return DbmDeliveryStore.FileWriter(dbm,
                self._get_key(filemeta_obj))

    def remove(self, filemeta_obj):
        dbm = self.dbm.open(self.filename, 'c')
        key = self._get_key(filemeta_obj)
        if not key in dbm:
            raise FileNotFoundError(filemeta_obj)
        del dbm[key]

    def exists(self, filemeta_obj):
        dbm = self.dbm.open(self.filename, 'c')
        return self._get_key(filemeta_obj) in dbm


class MemoryDeliveryStore(DeliveryStoreInterface):
    """ Memory-base DeliveryStore ONLY FOR TESTING.

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
