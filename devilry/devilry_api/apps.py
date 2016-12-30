# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals
from django.apps import AppConfig


class DevilryAPIAppConfig(AppConfig):
    name = 'devilry.devilry_api'
    verbose_name = "Devilry api"

    def ready(self):
        from django_cradmin.superuserui import superuserui_registry
        from devilry.devilry_api.feedbackset_download.backends import DevilryApiZipBackend
        from ievv_opensource.ievv_batchframework import batchregistry
        from devilry.devilry_compressionutil import backend_registry
        from devilry.devilry_group import tasks
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_api'))
        appconfig.add_all_models()

        # add zip backend to registry
        backend_registry.Registry.get_instance().add(DevilryApiZipBackend)

        # add actiongroup for zipping groupcomment files to registry
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name='batchframework_api_compress_groupcomment',
                mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                actions=[
                    tasks.GroupCommentCompressAction
                ]))

        # add actiongroup for zipping all files in a feedbackset to registry
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name='batchframework_api_compress_feedbackset',
                mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
                actions=[
                    tasks.FeedbackSetCompressAction
                ]))
