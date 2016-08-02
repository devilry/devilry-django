from devilry.devilry_ziputil.backends.backends_base import PythonZipFileBackend

from django.conf import settings

import os


class MockDevilryZipBackend(PythonZipFileBackend):
    """
    Used for testing.
    """
    backend_id = 'default'

    @classmethod
    def get_storage_location(cls):
        return settings.DEVILRY_GROUP_ZIPFILE_DIRECTORY

    def __init__(self, **kwargs):
        super(MockDevilryZipBackend, self).__init__(**kwargs)
        self.__create_path_if_not_exists()

    def __create_path_if_not_exists(self):
        """
        Create path if given path does not exist.
        """
        if os.path.exists(self.archive_path):
            return
        path_list = self.archive_path.split('/')
        path_list.pop()
        pathbuilder = ''
        for path in path_list:
            pathbuilder += path + '/'
            if not os.path.exists(pathbuilder):
                os.mkdir(pathbuilder)


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
