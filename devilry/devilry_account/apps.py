from django.apps import AppConfig
from django.utils.translation import ugettext_lazy
from django_cradmin.superuserui import superuserui_registry


class AccountAppConfig(AppConfig):
    name = 'devilry.devilry_account'
    verbose_name = ugettext_lazy("Devilry account")

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_account'))
        # page_model = self.get_model('Page')
        # appconfig.add_model(superuserui_registry.ModelConfig(model_class=page_model))
        appconfig.add_all_models()
