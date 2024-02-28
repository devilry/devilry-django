import os

from devilry.devilry_compressionutil.backends import backends_base


class DevilryAdminZipBackend(backends_base.StreamZipBackend):
    backend_id = 'devilry_admin_local'

    @classmethod
    def delete_archive(cls, full_path):
        if self.save_to_disk:
            if not os.path.exists(full_path):
                return False
            try:
                os.remove(full_path)
            except OSError:
                return False
            return True
        else:
            return False
