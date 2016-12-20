# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals
from django.apps import AppConfig


class DevilryAPIAppConfig(AppConfig):
    name = 'devilry.devilry_api'
    verbose_name = "Devilry api"

    def ready(self):
        from django_cradmin.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_api'))
        appconfig.add_all_models()
