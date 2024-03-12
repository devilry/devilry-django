import os

from devilry.devilry_compressionutil.backends import backends_base



class DevilryExaminerZipBackend(backends_base.StreamZipBackend):
    backend_id = 'devilry_examiner_local'

    @classmethod
    def delete_archive(cls, full_path):
        if not os.path.exists(full_path):
            return False
        try:
            os.remove(full_path)
        except OSError:
            return False
        return True
