from django.apps import AppConfig
from django.utils.translation import ugettext_lazy
from django_cradmin.superuserui import superuserui_registry


class DevilryGroupAppConfig(AppConfig):
    name = 'devilry.devilry_group'
    verbose_name = "Devilry group"

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_group'))
        appconfig.add_all_models()
