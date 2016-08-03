import os

from django.conf import settings

from devilry.devilry_ziputil.backends import backends_base


class DevilryGroupZipBackend(backends_base.PythonZipFileBackend):
    """
    Implementation of backend used by devilry group.
    """
    backend_id = 'devilry_group_local'

    def __init__(self, **kwargs):
        super(DevilryGroupZipBackend, self).__init__(**kwargs)
        self.__create_path_if_not_exists()

    def __create_path_if_not_exists(self):
        """
        Create path if given path does not exist.
        """
        archivedirname = os.path.dirname(self.archive_path)
        if not os.path.exists(archivedirname):
            os.makedirs(archivedirname)
