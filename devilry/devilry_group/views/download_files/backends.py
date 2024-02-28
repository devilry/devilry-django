# Python imports
import os

# Devilry imports
from devilry.devilry_compressionutil.backends import backends_base


class DevilryGroupZipBackend(backends_base.StreamZipBackend):
    """
    Implementation of backend used by devilry group.
    """
    backend_id = 'devilry_group_local'
    save_to_disk = False

    def __init__(self, **kwargs):
        super(DevilryGroupZipBackend, self).__init__(**kwargs)

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
        return False
