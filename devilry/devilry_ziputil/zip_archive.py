import os
import zipfile


class ZipArchive(object):
    """

    """
    def __init__(self, archive_path):
        """

        Args:
            archive_name:

        Returns:

        """
        self.archive_name = archive_path
        self.archive = zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED)

    def write(self, path, filelike_obj):
        """

        Args:
            path (str):
            filelike_obj (ReadableInterface):
        """
        self.archive.writestr(path, filelike_obj.read())

    def archive_size(self):
        """Get size of archive.

        Returns:
            int: size of archive.
        """
        return os.stat(self.archive_name).st_size

    def get_archive(self):
        """Closes the Zip archive and returns it.

        Returns:
            ZipFile: Zipped archive.
        """
        self.archive.close()
        return self.archive
