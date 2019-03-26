from django.apps import AppConfig


class DevilryCompressionUtilAppConfig(AppConfig):
    name = 'devilry.devilry_compressionutil'
    verbose_name = 'Devilry compression utilities'

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label='devilry_compressionutil')
        )
        appconfig.add_all_models()
