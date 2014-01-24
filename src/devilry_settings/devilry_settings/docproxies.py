from django_decoupled_docs.registry import VersionedReadTheDocsDocProxyBase
from devilry.version import devilry_version



class DevilryUserDocsProxy(VersionedReadTheDocsDocProxyBase):
    projectname = 'devilry-userdoc'

    def get_current_version(self):
        return devilry_version