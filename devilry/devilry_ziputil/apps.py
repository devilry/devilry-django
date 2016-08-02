from django.apps import AppConfig

from devilry.devilry_ziputil import backend_registry


class DevilryZipAppConfig(AppConfig):
    name = 'devilry.devilry_ziputil'
    verbose_name = "Devilry zip utility"

    def ready(self):
        from devilry.devilry_group.views.download_files import backends as group_backends
        backend_registry.Registry.get_instance().add(group_backends.DevilryGroupZipBackend)
