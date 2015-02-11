from devilry.django_decoupled_docs.registry import VersionedReadTheDocsDocProxyBase
import devilry


class DevilryDocsProxy(VersionedReadTheDocsDocProxyBase):
    projectname = 'devilry'

    def get_current_version(self):
        return devilry.__version__
