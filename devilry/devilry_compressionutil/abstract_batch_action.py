# -*- coding: utf-8 -*-


import os
from ievv_opensource.ievv_batchframework import batchregistry


class AbstractBaseBatchAction(batchregistry.Action):
    """
    """
    #: Backend id to get from registry in function `get_backend()`.
    #: Must be set in subclass.
    backend_id = ''

    def get_backend(self, zipfile_path, archive_name):
        """
        Get and instance of the backend to use.

        Args:
            zipfile_path: Path to the archive.
            archive_name: Name of the archive.

        Returns:
            PythonZipFileBackend: Backend for `self.backend_id`
        """
        from devilry.devilry_compressionutil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get(self.backend_id)
        return zipfile_backend_class(
            archive_path=zipfile_path,
            archive_name=archive_name,
            readmode=False
        )



    def execute(self):
        raise NotImplementedError()
