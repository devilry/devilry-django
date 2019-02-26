# -*- coding: utf-8 -*-


from django.apps import AppConfig


class DevilryAdminAppConfig(AppConfig):
    name = 'devilry.devilry_admin'
    verbose_name = 'Devilry admin'

    def ready(self):
        from devilry.devilry_admin.views.assignment.download_files import backends
        from devilry.devilry_compressionutil import backend_registry
        from ievv_opensource.ievv_batchframework import batchregistry
        from devilry.devilry_report import generator_registry as report_generator_registry
        from devilry.devilry_admin.views.period import all_results_generator
        from devilry.devilry_admin import tasks

        backend_registry.Registry.get_instance().add(backends.DevilryAdminZipBackend)

        # Add zip backend to registry
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name='batchframework_admin_compress_assignment',
                mode=batchregistry.ActionGroup.MODE_ASYNCHRONOUS,
                actions=[
                    tasks.AssignmentCompressAction
                ]))

        # All period-all-results-generator to the registry.
        report_generator_registry.Registry.get_instance().add(
            generator_class=all_results_generator.AllResultsExcelReportGenerator
        )
