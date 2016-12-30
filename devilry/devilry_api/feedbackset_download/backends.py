from devilry.devilry_compressionutil.backends import backends_base


class DevilryApiZipBackend(backends_base.PythonZipFileBackend):

    backend_id = 'devilry_api_local'

    def __init__(self, **kwargs):
        super(DevilryApiZipBackend, self).__init__(**kwargs)

