# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.apps import AppConfig


class DevilryQualifiesForExamAppConfig(AppConfig):
    name = 'devilry.devilry_qualifiesforexam'
    verbose_name = 'Devilry qualifies for exam'

    def ready(self):
        # Add models to cradmin superuserui
        from django_cradmin.superuserui import superuserui_registry
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_qualifiesforexam'))
        appconfig.add_all_models()
