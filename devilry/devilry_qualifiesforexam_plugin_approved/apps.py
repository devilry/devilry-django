# -*- coding: utf-8 -*-


# Django imports
from django.apps import AppConfig


class DevilryQualifiesForExamApprovedAppConfig(AppConfig):
    name = 'devilry.devilry_qualifiesforexam_plugin_approved'
    verbose_name = 'Devilry qualifies for exam plugin approved'

    def ready(self):
        from devilry.devilry_qualifiesforexam import plugintyperegistry
        from . import plugin
        plugintyperegistry.Registry.get_instance().add(plugin.SelectAssignmentsPlugin)
