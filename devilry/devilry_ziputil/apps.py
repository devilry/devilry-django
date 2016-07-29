from django.apps import AppConfig


class DevilryZipAppConfig(AppConfig):
    name = 'devilry.devilry_ziputil'
    verbose_name = "Devilry zip utility"

    def ready(self):
        # TODO: Add singleton backends to registry.
        pass
