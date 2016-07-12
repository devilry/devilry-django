# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals
from django.apps import AppConfig
from django_cradmin.superuserui import superuserui_registry


class DevilryAPIAppConfig(AppConfig):
    name = 'devilry.devilry_api'
    verbose_name = "Devilry api"

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_api'))
        appconfig.add_all_models()

