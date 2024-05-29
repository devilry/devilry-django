import os

from devilry.devilry_compressionutil.backends import backends_base


class DevilryExaminerZipBackend(backends_base.PythonZipFileBackend):
    backend_id = 'devilry_examiner_local'
