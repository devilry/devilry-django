# Django imports
from django.apps import AppConfig


class DevilryQualifiesForExamAppConfig(AppConfig):
    name = 'devilry.devilry_qualifiesforexam'
    verbose_name = 'Devilry qualifies for exam'

    def ready(self):
        from devilry.devilry_qualifiesforexam import plugintyperegistry
        from devilry.devilry_qualifiesforexam.plugins import plugin_select
        from devilry.devilry_qualifiesforexam.plugins import plugin_points
        plugintyperegistry.Registry.get_instance().add(plugin_select.SelectPlugin)
        plugintyperegistry.Registry.get_instance().add(plugin_points.PointsPlugin)
