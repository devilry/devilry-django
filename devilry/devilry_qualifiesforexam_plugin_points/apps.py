# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.apps import AppConfig


class DevilryQualifiesForExamPointsAppConfig(AppConfig):
    name = 'devilry.devilry_qualifiesforexam_plugin_points'
    verbose_name = 'Devilry qualifies for exam plugin points'

    def ready(self):
        from devilry.devilry_qualifiesforexam import plugintyperegistry
        from . import plugin
        plugintyperegistry.Registry.get_instance().add(plugin.PointsPlugin)
