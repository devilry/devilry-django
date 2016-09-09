from django.apps import AppConfig

from devilry.devilry_compressionutil import backend_registry


class DevilryZipAppConfig(AppConfig):
    name = 'devilry.devilry_compressionutil'
    verbose_name = "Devilry compression utilities"

    def ready(self):
        from devilry.devilry_group.views.download_files import backends as group_backends
        backend_registry.Registry.get_instance().add(group_backends.DevilryGroupZipBackend)
