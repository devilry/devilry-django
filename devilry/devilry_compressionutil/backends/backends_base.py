# Python imports
import os
import posixpath
import zipfile

# Django imports
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage, Storage, storages

from devilry.utils.memorydebug import print_memory_usage


class BaseArchiveBackend(object):
    """
    Specifies the interface for a backend compression-subclass.

    All backends must implement this class.
    """

    #: A unique string ID for the subclasses to use that describes what kind of backend it is.
    backend_id = None

    class Meta:
        abstract = True

    def __init__(self, archive_path, archive_name='', readmode=True):
        """

        Args:
            archive_path: Full path to archive including the archive name.
            archive_name: Only the archive name.
            readmode: Can be read from, defaults to ``True``.

        """
        self.archive_path = archive_path
        self.archive_name = archive_name
        self.readmode = readmode
        self._closed = False
        if not self.archive_name.endswith(self.get_archive_file_extension()):
            self.archive_name += self.get_archive_file_extension()
        if not self.archive_path.endswith(self.get_archive_file_extension()):
            self.archive_path += self.get_archive_file_extension()

    @classmethod
    def get_storage_backend(cls) -> Storage:
        return storages[settings.DEVILRY_COMPRESSED_ARCHIVES_STORAGE_BACKEND]

    @property
    def storage_backend(self) -> Storage:
        return self.__class__.get_storage_backend()

    @classmethod
    def get_storage_directory(cls) -> str:
        """
        Get the storage location for archives.

        Returns:
            str: Location specified in settings ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY``.
        """
        return settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY

    @classmethod
    def delete_archive(cls, archive_path: str):
        """
        Deletes the archive.

        Args:
            full_path (str): Full path to the stored archive.
        """
        cls.get_storage_backend().delete(posixpath.join(cls.get_storage_directory(), archive_path))

    @property
    def archive_full_path(self) -> str:
        return posixpath.join(self.__class__.get_storage_directory(), self.archive_path)

    def _create_directory_if_not_exists(self):
        """
        Create if it does not exist.
        """
        if isinstance(self.storage_backend, FileSystemStorage):
            directory_path = os.path.dirname(
                self.storage_backend.path(self.archive_full_path))
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

    def open_read_binary(self) -> File:
        """
        Opens archive in read binary mode.
        Best suited for non-text files like images, videos etc or when serving file for download.

        Returns:
            file: file object in read binary mode.

        Raises:
            ValueError: If archive is ``None``, or ``readmode`` is False.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return self.storage_backend.open(self.archive_full_path, 'rb')

    def open_write_binary(self) -> File:
        """
        Opens archive in write binary mode.

        Returns:
            file: file object in read binary mode.

        Raises:
            ValueError: If archive is ``None``, or ``readmode`` is False.
        """
        if self.readmode:
            raise ValueError('Must NOT be in readmode')
        self._create_directory_if_not_exists()
        return self.storage_backend.open(self.archive_full_path, 'wb')

    def close(self):
        """
        Close archive when done with adding files to it.

        Raises:
            ValueError: If ``archive`` is ``None``.
        """
        self._closed = True

    def archive_exists(self) -> bool:
        """
        Check if the archive exists in the storage backend.

        Returns:
            bool: Does the archive exist in the storage backend?
        """
        return self.storage_backend.exists(self.archive_full_path)

    def archive_size(self) -> int:
        """
        Get size of archive. Uses ``os.stat``.

        Returns:
            int: size of archive.
        """
        return self.storage_backend.size(self.archive_full_path)

    def add_file(self, path, filelike_obj):
        """
        Add file to archive.

        Args:
            path (str): Path to the file inside the archive.
            filelike_obj: An object which implements function ``read()``.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError()

    def read_archive(self):
        """
        Should return a object of the underlying compression tool in readmode.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError()

    def get_archive_file_extension(self) -> str:
        raise NotImplementedError()

    def get_content_type(self) -> str:
        raise NotImplementedError()


class PythonZipFileBackend(BaseArchiveBackend):
    """
    Defines a baseclass backend using :class:`~ZipFile`
    for the :class:`~devilry.devilry_ziputil.backend_registry.Registry`.

    This class should be subclassed by backend-specific classes(backends for Heroku, S3, etc).
    """
    def __init__(self, **kwargs):
        super(PythonZipFileBackend, self).__init__(**kwargs)
        self._archive = None

    def get_archive_file_extension(self) -> str:
        return '.zip'

    def add_file(self, path, filelike_obj):
        """
        Add files to archive.

        Args:
            path (str): Path to the file inside the Zip-archive.
            filelike_obj: An object with method ``read()``

        Raises:
            ValueError: If ``readmode`` is set to ``True``, must be ``False`` to add files.
        """
        if self.readmode is True:
            raise ValueError('readmode must be False to add files.')
        if self._archive is None or self._closed:
            self._closed = False
            self._archive = zipfile.ZipFile(
                self.open_write_binary(), 'a', zipfile.ZIP_DEFLATED, allowZip64=True)
        print_memory_usage(f'Before adding {path} to zipfile')
        CHUNK_SIZE = 1024 * 1024 * 8  # 8MB
        with self._archive.open(path, 'w', force_zip64=True) as destinationfile:
            while True:
                # print_memory_usage(f'Before reading chunk from {path}')
                chunk = filelike_obj.read(CHUNK_SIZE)
                # print_memory_usage(f'After reading chunk from {path}')
                if chunk:
                    destinationfile.write(chunk)
                    # print_memory_usage(f'After writing chunk from {path}')
                else:
                    break
        print_memory_usage(f'After adding {path} to zipfile')

    def read_archive(self):
        """
        Get the zipped archive as :obj:`~ZipFile` in readmode.

        Returns:
            ZipFile: The zipped archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return zipfile.ZipFile(self.open_read_binary(), 'r', allowZip64=True)

    def get_content_type(self) -> str:
        return 'application/zip'

    def close(self):
        super().close()
        if self._archive:
            self._archive.close()
            self._archive = None
