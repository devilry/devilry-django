import os
import zipfile


class BaseZipFile(object):
    """

    """
    def __init__(self, archive_path, readmode=True):
        self.archive_path = archive_path
        self.readmode = readmode

    def add_file(self, path, filelike_obj):
        """

        Args:
            path:
            filelike_obj:

        Returns:

        """
        raise NotImplementedError()

    def get_fileobject(self):
        """

        Returns:

        """
        raise NotImplementedError()

    def archive_size(self):
        """

        Returns:

        """
        raise NotImplementedError()


class PythonZipFileBackend(BaseZipFile):
    """

    """
    def __init__(self, **kwargs):
        """

        Args:
            archive_name:

        Returns:

        """
        super(PythonZipFileBackend, self).__init__(**kwargs)
        self.__archive = None

    def add_file(self, path, filelike_obj):
        """

        Args:
            path (str):
            filelike_obj (ReadableInterface):
        """
        if self.__archive is None:
            self.__archive = zipfile.ZipFile(self.archive_path, 'w', zipfile.ZIP_DEFLATED)
        self.__archive.writestr(path, filelike_obj.read())

    def get_fileobject(self):
        """

        Returns:

        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return open(self.__archive, 'rb')

    def archive_size(self):
        """Get size of archive.

        Returns:
            int: size of archive.
        """
        if not self.readmode:
            raise ValueError('Must be in readmode')
        return os.stat(self.archive_path).st_size
