# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

    def add_file(self, zipfile_backend, sub_path, comment_file, is_duplicate=False):
        """
        Add file to ZIP archive.

        Args:
            zipfile_backend: A subclass of ``PythonZipFileBackend``.
            sub_path: The path to write to inside the archive.
            comment_file: The `CommentFile` file to write.
            is_duplicate: Is the file a duplicate? Defaults to ``False``.
        """
        file_name = comment_file.filename
        if is_duplicate:
            file_name = comment_file.get_filename_as_unique_string()

        zipfile_backend.add_file(
            os.path.join(sub_path, file_name),
            comment_file.file.file)

    def execute(self):
        raise NotImplementedError()