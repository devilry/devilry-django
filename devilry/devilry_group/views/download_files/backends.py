# Python imports
import os

# Devilry imports
from devilry.devilry_compressionutil.backends import backends_base


class DevilryGroupZipBackend(backends_base.PythonZipFileBackend):
    """
    Implementation of backend used by devilry group.
    """
    backend_id = 'devilry_group_local'

    def __init__(self, **kwargs):
        super(DevilryGroupZipBackend, self).__init__(**kwargs)
