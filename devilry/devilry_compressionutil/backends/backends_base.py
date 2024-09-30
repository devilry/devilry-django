# Python imports
import os
import posixpath
import tarfile

# Django imports
from django.conf import settings
from django.core.files import File
from django.core.files import File as DjangoFile
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.functional import cached_property
from storages.backends.s3 import S3Storage

from devilry.utils.memorydebug import print_memory_usage
from devilry.utils.storageutils import (
    get_temporary_storage,
    get_temporary_storage_generate_urls,
)


class BaseArchiveBackend(object):
    """
    Specifies the interface for a backend compression-subclass.

    All backends must implement this class.
    """

    #: A unique string ID for the subclasses to use that describes what kind of backend it is.
    backend_id = None

    class Meta:
        abstract = True

    def __init__(self, archive_path, archive_name="", readmode=True):
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
        return get_temporary_storage()

    @classmethod
    def get_storage_backend_generate_urls(cls) -> Storage:
        return get_temporary_storage_generate_urls()

    @property
    def storage_backend(self) -> Storage:
        return self.__class__.get_storage_backend()

    @property
    def storage_backend_generate_urls(self) -> Storage:
        return self.__class__.get_storage_backend_generate_urls()

    @cached_property
    def storage_backend_url_is_secure(self) -> bool:
        """
        Check if storage backend can produce secure (private) urls that only the requesting user
        can gain access to.
        """
        if isinstance(self.storage_backend, S3Storage):
            return True
        return False

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
            directory_path = os.path.dirname(self.storage_backend.path(self.archive_full_path))
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
            raise ValueError("Must be in readmode")
        return self.storage_backend.open(self.archive_full_path, "rb")

    def get_secure_url(self) -> str:
        if self.storage_backend_url_is_secure:
            return self.storage_backend_generate_urls.url(self.archive_full_path)
        else:
            storage = self.__class__.get_storage_backend()
            raise ValueError(
                f"Storage backend, {storage.__module__}.{storage.__class__.__name__} can not produce safe download URLs"
            )

    def open_write_binary(self) -> File:
        """
        Opens archive in write binary mode.

        Returns:
            file: file object in read binary mode.

        Raises:
            ValueError: If archive is ``None``, or ``readmode`` is False.
        """
        if self.readmode:
            raise ValueError("Must NOT be in readmode")
        self._create_directory_if_not_exists()
        return self.storage_backend.open(self.archive_full_path, "wb")

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

    def add_file(self, path, djangofile: DjangoFile):
        """
        Add files to archive.

        Args:
            path (str): Path to the file inside the Zip-archive.
            djangofile: An django.core.files.File object.
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
        return ".tar.gz"

    def add_file(self, path, djangofile: DjangoFile):
        if self.readmode is True:
            raise ValueError("readmode must be False to add files.")
        if self._archive is None or self._closed:
            self._closed = False
            self._archivefile = self.open_write_binary()
            self._archive = tarfile.open(mode="w:gz", fileobj=self._archivefile)
        print_memory_usage(f"Before adding {path} to tarfile")
        # CHUNK_SIZE = 1024 * 1024 * 8  # 8MB
        with djangofile.open("rb") as inputfile:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = djangofile.size
            self._archive.addfile(tarinfo=tarinfo, fileobj=inputfile)
        print_memory_usage(f"After adding {path} to tarfile")

    def read_archive(self):
        """
        Get the zipped archive as :obj:`~TarFile` in readmode.

        Returns:
            TarFile: The zipped archive.
        """
        if not self.readmode:
            raise ValueError("Must be in readmode")
        return tarfile.open(mode="r:gz", fileobj=self.open_read_binary())

    def get_content_type(self) -> str:
        return "application/x-gzip"

    def close(self):
        super().close()
        if self._archive:
            self._archive.close()
            self._archivefile.close()
            self._archive = None
            self._archivefile = None
