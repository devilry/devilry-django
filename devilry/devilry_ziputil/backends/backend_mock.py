from devilry.devilry_ziputil.backends.backends_base import PythonZipFileBackend

from django.conf import settings

import os


class MockDevilryZipBackend(PythonZipFileBackend):
    """
    Used for testing.
    """
    backend_id = 'default'

    def __init__(self, **kwargs):
        super(MockDevilryZipBackend, self).__init__(**kwargs)
        self.__create_path_if_not_exists()

    def __create_path_if_not_exists(self):
        """
        Create path if given path does not exist.
        """
        archivedirname = os.path.dirname(self.archive_path)
        if not os.path.exists(archivedirname):
            os.makedirs(archivedirname)

    def get_path(self):
        """
        Get the archive path. Used for testing.
        """
        return self.archive_path


class MockDevilryZipBackendS3(MockDevilryZipBackend):
    """

    """
    backend_id = 's3'

    @classmethod
    def get_storage_location(cls):
        return 'url/to/s3/filestorage'

    def __init__(self, **kwargs):
        super(MockDevilryZipBackendS3, self).__init__(**kwargs)


class MockDevilryZipBackendHeroku(MockDevilryZipBackend):
    """

    """
    backend_id = 'heroku'

    @classmethod
    def get_storage_location(cls):
        return 'url/to/heroku/filestorage'

    def __init__(self, **kwargs):
        super(MockDevilryZipBackendHeroku, self).__init__(**kwargs)
