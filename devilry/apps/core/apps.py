from django.apps import AppConfig
from django.utils.translation import ugettext_lazy
from django_cradmin.superuserui import superuserui_registry


class CoreAppConfig(AppConfig):
    name = 'devilry.apps.core'
    verbose_name = ugettext_lazy("Devilry core")

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='core'))
        appconfig.add_all_models()
