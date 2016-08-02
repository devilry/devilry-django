import os

from django.conf import settings

from devilry.devilry_ziputil.backends import backends_base


class DevilryGroupZipBackend(backends_base.PythonZipFileBackend):
    """

    """
    backend_id = 'devilry_group_local'

    @classmethod
    def get_storage_location(cls):
        return settings.DEVILRY_GROUP_ZIPFILE_DIRECTORY

    def __init__(self, **kwargs):
        super(DevilryGroupZipBackend, self).__init__(**kwargs)
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
