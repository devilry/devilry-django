from django.apps import AppConfig


class MultiselectdemoConfig(AppConfig):
    name = "cradmin_legacy.demo.multiselect2demo"
    verbose_name = "Multiselect demo"

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry

        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label="multiselect2demo")
        )
        appconfig.add_all_models()
