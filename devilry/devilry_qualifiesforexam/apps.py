# # Django imports
# from django.apps import AppConfig
#
#
# class DevilryQualifiesForExamAppConfig(AppConfig):
#     name = 'devilry.devilry_qualifiesforexam'
#     verbose_name = 'Devilry qualifies for exam'
#
#     def ready(self):
#         from devilry.devilry_qualifiesforexam import plugintyperegistry
#         from devilry.devilry_qualifiesforexam_plugin_approved import plugin
#         plugintyperegistry.Registry.get_instance().add(plugin.SelectAssignmentsPlugin)
