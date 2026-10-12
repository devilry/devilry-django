from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class ImageArchiveConfig(AppConfig):
    name = "cradmin_legacy.apps.cradmin_imagearchive"
    verbose_name = gettext_lazy("Image archive")

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry

        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label="cradmin_imagearchive")
        )
        appconfig.add_all_models()
