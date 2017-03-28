# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DevilryGroupAppConfig(AppConfig):
    name = 'devilry.devilry_group'
    verbose_name = "Devilry group"

    def ready(self):
        # Add models to cradmin superuserui
        from django_cradmin.superuserui import superuserui_registry
        from devilry.devilry_group.views.download_files import backends
        from devilry.devilry_compressionutil import backend_registry
        from ievv_opensource.ievv_batchframework import batchregistry
        from devilry.devilry_group import tasks
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_group'))
        appconfig.add_all_models()

        # add zip backend to registry
        backend_registry.Registry.get_instance().add(backends.DevilryGroupZipBackend)

        # add actiongroup for zipping all files in a feedbackset to registry
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name='batchframework_compress_feedbackset',
                mode=batchregistry.ActionGroup.MODE_ASYNCHRONOUS,
                actions=[
                    tasks.FeedbackSetCompressAction
                ]))
