from django.conf import settings
from devilry.django_decoupled_docs.registry import VersionedReadTheDocsDocProxyBase
import devilry


class DevilryDocsProxy(VersionedReadTheDocsDocProxyBase):
    projectname = 'devilry'

    def get_current_version(self):
        return settings.DEVILRY_DOCUMENTATION_VERSION
