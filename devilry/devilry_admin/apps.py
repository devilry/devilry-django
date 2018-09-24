# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DevilryAdminAppConfig(AppConfig):
    name = 'devilry.devilry_admin'
    verbose_name = 'Devilry admin'

    def ready(self):
        from devilry.devilry_admin.views.assignment.download_files import backends
        from devilry.devilry_compressionutil import backend_registry
        from ievv_opensource.ievv_batchframework import batchregistry
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
