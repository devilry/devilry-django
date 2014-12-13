from django_decoupled_docs.registry import VersionedReadTheDocsDocProxyBase
import devilry



class DevilryUserDocsProxy(VersionedReadTheDocsDocProxyBase):
    projectname = 'devilry-userdoc'

    def get_current_version(self):
        return devilry.__version__
