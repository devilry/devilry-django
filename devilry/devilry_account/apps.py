from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class AccountAppConfig(AppConfig):
    name = 'devilry.devilry_account'
    verbose_name = gettext_lazy("Devilry account")

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_account'))
        # page_model = self.get_model('Page')
        # appconfig.add_model(superuserui_registry.ModelConfig(model_class=page_model))
        appconfig.add_all_models()
