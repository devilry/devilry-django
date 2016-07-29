from devilry.devilry_ziputil.backends.backends_base import PythonZipFileBackend

from django.conf import settings


class MockDevilryZipBackend(PythonZipFileBackend):
    """

    """
    backend_id = 'default'

    @classmethod
    def get_storage_location(cls):
        return settings.DEVILRY_GROUP_ZIPFILE_DIRECTORY

    def __init__(self, **kwargs):
        super(MockDevilryZipBackend, self).__init__(**kwargs)


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
