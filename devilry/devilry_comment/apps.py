# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django_cradmin.superuserui import superuserui_registry


class DevilryCommentAppConfig(AppConfig):
    name = 'devilry.devilry_comment'
    verbose_name = "Devilry comment"

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label='devilry_comment'))
        appconfig.add_all_models()
