# -*- coding: utf-8 -*-


from django.apps import AppConfig


class DevilryCommentAppConfig(AppConfig):
    name = 'devilry.devilry_comment'
    verbose_name = "Devilry comment"

    def ready(self):
        from cradmin_legacy.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label='devilry_comment'))
        appconfig.add_all_models()
