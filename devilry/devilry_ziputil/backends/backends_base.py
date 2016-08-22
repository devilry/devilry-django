import os
import zipfile

from django.conf import settings


class BaseArchiveBackend(object):
    """
    Specifies the interface for a backend compression-subclass.

    All backends must implement this class
    """
    class Meta:
        abstract = True

    def __init__(self, archive_path, archive_name='', readmode=True):
        self.archive_path = archive_path
        self.archive_name = archive_name
        self.readmode = readmode
        self.__closed = False

    def add_file(self, path, filelike_obj):
        """
        Add files to archive.
        """
        raise NotImplementedError()

    def close_archive(self):
        """
        Close archive.
        """
        raise NotImplementedError()

    def read_archive(self):
        """
        Open archive in readmode.

        Returns:
            File object: Python fileobject.
        """
        raise NotImplementedError()

    def get_archive(self):
        """
        Get the Zip archive

        Returns:
            ZipFile: Zip-archive created.
        """
        raise NotImplementedError()

    def archive_size(self):
        """
        Get the size of the compressed Zip-archive.

        Return:
            int: Size of the Zip-archive.
        """
        raise NotImplementedError()


class PythonZipFileBackend(BaseArchiveBackend):
    """
    Defines a baseclass backend using :class:`~ZipFile`
    for the :class:`~devilry.devilry_ziputil.backend_registry.Registry`.

    This class should be subclassed by backend-specific classes(backends for Heroku, S3, etc).
    """

    #: A unique string ID for the subclasses to use that describes what kind of backend that
    #: is used and is the identifier for a registry-class. Example IDs ``s3``, ``heroku`` etc.
    backend_id = None

    @classmethod
    def get_storage_location(cls):
        return settings.DEVILRY_ZIPFILE_DIRECTORY

    def __init__(self, **kwargs):
        super(PythonZipFileBackend, self).__init__(**kwargs)
        self.__archive = None
        self.__add_path_extension()

    def __add_path_extension(self):
        """
        Sets :obj:`~.PythonZipFileBackend.archive_path` to full path by prepending the backend storage location
        to the archive_path. Also adds .zip extension
        """
        if not self.archive_path.endswith('.zip'):
            self.archive_name += '.zip'
            self.archive_path = PythonZipFileBackend.get_storage_location() + self.archive_path + '.zip'
        else:
            self.archive_path = PythonZipFileBackend.get_storage_location() + self.archive_path

    def add_file(self, path, filelike_obj):
        """
        Add files to archive. This function is used for writing to the archive.

        Args:
            path: Path to the file inside the Zip-archive.
            filelike_obj: An object with method ``read()``
        """
        if self.readmode is True:
            raise ValueError('readmode must be False to add files.')
        if self.__archive is None or self.__closed:
            self.__closed = False
            self.__archive = zipfile.ZipFile(self.archive_path, 'a', zipfile.ZIP_DEFLATED, allowZip64=True)
        self.__archive.writestr(path, filelike_obj.read())

    def read_archive(self):
        """
        Open archive in readmode as fileobject.

        ``readmode`` must be set to ``True`` with ``instance_of_this_class.readmode = True``.

        Returns:
            File object: Python fileobject.

        Raises:
            ValueError: Error when either archive does not exists, or ``readmode`` is ``False``.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.__archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return open(self.archive_path, mode='rb')

    def close_archive(self):
        """
        Close zipfile when done with adding files to it.
        """
        if not self.__archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        self.__closed = True
        self.__archive.close()

    def get_archive(self):
        """
        Get the zipped archive.

        Returns:
            ZipFile: The zipped archive.
        """
        return zipfile.ZipFile(self.archive_path, 'r', allowZip64=True)

    def archive_size(self):
        """
        Get size of archive.

        Returns:
            int: size of archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.__archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return os.stat(self.archive_path).st_size
