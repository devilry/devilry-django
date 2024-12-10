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


class StreamZipBackend(BaseArchiveBackend):
    def __init__(self, save_to_disk=False, chunk_size=None, **kwargs):
        super(StreamZipBackend, self).__init__(**kwargs)
        self.files = []
        self.zipped_chunks = None
        self.save_to_disk = save_to_disk
        self.__add_path_extension()
        self._create_path_if_not_exists()
        if chunk_size:
            self.chunk_size = chunk_size
        else:
            self.chunk_size = int(0x8000)

    def __add_path_extension(self):
        """
        Sets :obj:`~.PythonZipFileBackend.archive_path` to full path by prepending the backend storage location
        to the archive_path. Also adds .zip extension
        """
        if self.save_to_disk:
            self.archive_path = os.path.join(self.get_storage_location(), self.archive_path)
        if not self.archive_path.endswith('.zip'):
            self.archive_name += '.zip'
            self.archive_path += '.zip'

    def archive_size(self):
        """
        Get size of archive. Uses ``os.stat``.

        Returns:
            int: size of archive.

        Raises:
            ValueError: If not in ``readmode``.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return 0

    def add_file(self, path, filelike_obj):
        """
        Prep a file to be written to the archive on the given ``path``.

        Args:
            path: Path to file inside the archive.
            filelike_obj: An object that behaves like a File(read, write..).

        """
        if self.readmode is True:
            raise ValueError('readmode must be False to add files.')

        self.files.append((path, filelike_obj))

    def read_archive(self):
        """
        Get the zipped archive as :obj:`~ZipFile` in readmode.

        Returns:
            ZipFile: The zipped archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.zipped_chunks:
            raise ValueError('Archive has not been created yet')
        return zipfile.ZipFile(io.BytesIO(b''.join(self.zipped_chunks)))

    def get_archive(self):
        """
        Get the filelike object of the archive for compressed files.

        """
        return to_file_like_obj(self.zipped_chunks)

    def _prep_files(self):
        """
        Prepares the files for Zip creation
        """
        now = timezone.now()
        mode = S_IFREG | 0o600

        def contents(file_object):
            with file_object.file.open() as f:
                while chunk := f.read(self.chunk_size):
                    yield chunk

        for (path, filelike_obj) in self.files:
            yield (path, now, mode, ZIP_AUTO(filelike_obj.file.size), contents(filelike_obj))


    def close(self):
        """
        Must be invoked in order to process the files into an iterable yielding the bytes of the ZIP file.

        Readmode is set to True
        """
        prepped_files = self._prep_files()
        self.zipped_chunks = stream_zip(prepped_files, chunk_size=self.chunk_size)
        self.readmode = True

        if self.save_to_disk:
            self.archive = open(self.archive_path, 'wb')
            for chunk in self.zipped_chunks:
                self.archive.write(chunk)

            super(StreamZipBackend, self).close()

    def get_chunk_size(self):
        return self.chunk_size

    def _create_path_if_not_exists(self):
        """
        Create path if given path does not exist.
        """
        archivedirname = os.path.dirname(self.archive_path)
        if self.save_to_disk:
            if not os.path.exists(archivedirname):
                os.makedirs(archivedirname)


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
