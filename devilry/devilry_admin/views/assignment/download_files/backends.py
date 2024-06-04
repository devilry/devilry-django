import os

from devilry.devilry_compressionutil.backends import backends_base


class DevilryAdminZipBackend(backends_base.PythonZipFileBackend):
    backend_id = 'devilry_admin_local'
