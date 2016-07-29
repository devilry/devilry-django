import os
import zipfile


class BaseZipFile(object):
    """
    Specifies the interface for a subclass.
    """
    def __init__(self, archive_path, readmode=True):
        self.archive_path = archive_path
        self.readmode = readmode

    def add_file(self, path, filelike_obj):
        """
        Add files to archive.

        Args:
            path: Path to the file inside the Zip-archive.
            filelike_obj: An object with method ``read()``
        """
        raise NotImplementedError()

    def close_archive(self):
        """
        Close archive.
        """
        raise NotImplementedError()

    def open_archive(self):
        """
        Open archive in readmode.
        """
        raise NotImplementedError()

    def get_archive(self):
        """
        Get the Zip archive

        Return:
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


class PythonZipFileBackend(BaseZipFile):
    """
    Defines a baseclass backend for the :class:`~devilry.devilry_ziputil.backend_registry.Registry`.

    This class should be subclassed by backend-specific classes(backends for Heroku, S3, etc).
    """

    #: A unique string ID for the subclasses to use that describes what kind of backend that
    #: is used and is the identifier for a registry-class. Example IDs ``s3``, ``heroku`` etc.
    backend_id = None

    def __init__(self, **kwargs):
        super(PythonZipFileBackend, self).__init__(**kwargs)
        self.__archive = None

    def add_file(self, path, filelike_obj):
        """
        Add/write a file to the Zip-archive.

        Args:
            path (str):
            filelike_obj (ReadableInterface):
        """
        if self.__archive is None:
            self.__archive = zipfile.ZipFile(self.archive_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        self.__archive.writestr(path, filelike_obj.read())

    def open_archive(self):
        """
        Get archive in readmode if ``readmode`` is ``True``.
        For this to work, the archive must already exist.

        Returns:
            ZipFile: ZipFile ready for reading.

        Raises:
            ValueError: Error when either archive does not exists, or ``readmode`` is ``False``.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.__archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return zipfile.ZipFile(self.archive_path, 'r', allowZip64=True)

    def close_archive(self):
        """
        Close zipfile when done with adding files to it.
        """
        if not self.__archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        self.__archive.close()

    def get_archive(self):
        """
        Get the zipped archive.

        Returns:
            ZipFile: The zipped archive.
        """
        return self.__archive

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
