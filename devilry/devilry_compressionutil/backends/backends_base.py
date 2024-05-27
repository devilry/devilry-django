# Python imports
import os
import zipfile
import tarfile
import shutil

# Django imports
from django.conf import settings


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
        self.archive = None
        self.archive_path = archive_path
        self.archive_name = archive_name
        self.readmode = readmode
        self.__closed = False

    def get_storage_location(self):
        """
        Get the storage location for archives.

        Returns:
            str: Location specified in settings ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY``.
        """
        return settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY

    def _create_path_if_not_exists(self):
        """
        Create path if given path does not exist.
        """
        archivedirname = os.path.dirname(self.archive_path)
        if not os.path.exists(archivedirname):
            os.makedirs(archivedirname)

    def read_binary(self):
        """
        Opens archive in read binary mode.
        Best suited for non-text files like images, videos etc or when serving file for download.

        Returns:
            file: file object in read binary mode.

        Raises:
            ValueError: If archive is ``None``, or ``readmode`` is False.
        """
        if self.archive is None:
            raise ValueError('Archive is None')
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return open(self.archive_path, 'rb')

    def close(self):
        """
        Close archive when done with adding files to it.

        Raises:
            ValueError: If ``archive`` is ``None``.
        """
        if not self.archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        self.__closed = True
        self.archive.close()

    def archive_size(self):
        """
        Get size of archive. Uses ``os.stat``.

        Returns:
            int: size of archive.

        Raises:
            ValueError: If not in ``readmode`` or ``archive`` is ``None``.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return os.stat(self.archive_path).st_size

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

    def get_archive(self):
        """
        Get the archive for compressed files.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError()

    @classmethod
    def delete_archive(cls, full_path):
        """
        Deletes the archive.

        This must be implemented in subclass to handle the specifics for
        different storage backends.

        Args:
            full_path (str): Full path to the stored archive.

        Returns:
            (boolean): ``True`` if deleted, else ``False``.
        """
        raise NotImplementedError()


class PythonZipFileBackend(BaseArchiveBackend):
    """
    Defines a baseclass backend using :class:`~ZipFile`
    for the :class:`~devilry.devilry_ziputil.backend_registry.Registry`.

    This class should be subclassed by backend-specific classes(backends for Heroku, S3, etc).
    """
    def __init__(self, **kwargs):
        super(PythonZipFileBackend, self).__init__(**kwargs)
        self.__add_path_extension()
        self._create_path_if_not_exists()

    def __add_path_extension(self):
        """
        Sets :obj:`~.PythonZipFileBackend.archive_path` to full path by prepending the backend storage location
        to the archive_path. Also adds .zip extension
        """
        self.archive_path = os.path.join(self.get_storage_location(), self.archive_path)
        if not self.archive_path.endswith('.zip'):
            self.archive_name += '.zip'
            self.archive_path += '.zip'

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
        if self.archive is None or self.__closed:
            self.__closed = False
            self.archive = zipfile.ZipFile(self.archive_path, 'a', zipfile.ZIP_DEFLATED, allowZip64=True)
        self.archive.writestr(path, filelike_obj.read())

    def read_archive(self):
        """
        Get the zipped archive as :obj:`~ZipFile` in readmode.

        Returns:
            ZipFile: The zipped archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return zipfile.ZipFile(self.archive_path, 'r', allowZip64=True)


class PythonTarFileBackend(BaseArchiveBackend):
    """
    A baseclass backend using :class:`~TarFile` for archiving files to at tarball.
    Supports no compression, ``gzip`` and``bzip2`` compression through the :class:'~TarFile' class.
    """

    #: Compression formats supported.
    compression_formats = ['', 'gz', 'bz2']

    def __init__(self, stream=False, compression='', **kwargs):
        """

        Args:
            stream: If it should be handled as a stream or not.
            compression: The compression mode used, defaults to ``uncompressed``, but
                modes ``gz``, ``bz2`` and ``xz`` can also be used.

        """
        super(PythonTarFileBackend, self).__init__(**kwargs)
        self.__temp_path = os.path.join(
                '{}{}{}'.format(self.get_storage_location(), 'tempdir', self.archive_name), ''
        )
        os.makedirs(self.__temp_path)
        self.__stream = stream
        self.__compression = compression
        self.__add_path_extension()
        self._create_path_if_not_exists()

    def __add_path_extension(self):
        """
        Sets :obj:`~.PythonZipFileBackend.archive_path` to full path by prepending the backend storage location
        to the archive_path. Also adds .zip extension
        """
        self.archive_path = os.path.join(self.get_storage_location(), self.archive_path + '.tar')
        if self.__compression != '':
            self.archive_path += self.__compression

    def __check_compression_support(self):
        """
        Check that the ``compression`` specified is supported.

        Raises:
            ValueError: If compression format is not supported.
        """
        if self.__compression not in PythonTarFileBackend.compression_formats:
            raise ValueError('Unsupported compression format: {}'.format(self.__compression))

    def add_file(self, path, filelike_obj):
        """
        Writes a file to the archive on the given ``path``.

        In fact, this creates a temporary folder hierarchy which is zipped when ``closed()`` is invoked on a
        instance of this class.

        Args:
            path: Path to file inside the archive.
            filelike_obj: An object that behaves like a File(read, write..).

        """
        self.__check_compression_support()

        # Create path inside __tempdir
        folderpath, filename = os.path.split(path)
        sub_path = os.path.join(self.__temp_path, folderpath, '')
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        # Write file to temp directory.
        new_temp_file = open('{}{}'.format(sub_path, filename), 'a+')
        new_temp_file.write(filelike_obj.read())
        new_temp_file.close()

    def read_archive(self):
        """
        Get TarFile in readmode.

        Returns:
            TarFile: The compressed tar archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        if not self.archive:
            raise ValueError('Archive does not exist at {}'.format(self.archive_path))
        return tarfile.open(self.archive_path, mode='r')

    def __get_mode(self):
        """
        Get the mode the tarfile should be opened in.

        Here's an example of the writing modes without streaming::

            ``':'``    # writing without compression
            ``':gz'``  # writing with gzip compression
            ``':bz2'`` # writing with bz2 compression

        Here's an example of the writing modes with streaming::

            ``'|'``      # writing without compression
            ``'|gz'``    # writing with gzip compression
            ``'|bz2'``   # writing with bz2 compression

        Returns:
            mode (str): mode based on params passed to ``__init__``.
        """
        if self.__stream:
            return '|'+self.__compression
        return ':'+self.__compression

    def close(self):
        """
        Must be invoked in order to finalize the archive by compressing the 'temp' directory
        to whichever compression level specified.

        The temporary directory is then removed, and the tar archive is closed.
        """
        self.archive = tarfile.open(self.archive_path, mode='w' + self.__get_mode())
        self.archive.add(self.__temp_path, arcname=self.archive_name)

        # Remove temp directory.
        shutil.rmtree(self.__temp_path, ignore_errors=False)
        super(PythonTarFileBackend, self).close()

    def get_archive(self):
        """
        Get TarFile(archive) in read-mode.

        Returns:
            TarFile: Opened in read mode.

        """
        return tarfile.open(self.archive_path, 'r')
