from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class CoreAppConfig(AppConfig):
    name = 'devilry.apps.core'
    verbose_name = gettext_lazy("Devilry core")

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='core'))
        appconfig.add_all_models()
