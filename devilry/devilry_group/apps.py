# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from devilry.devilry_ziputil import backend_registry


class DevilryGroupAppConfig(AppConfig):
    name = 'devilry.devilry_group'
    verbose_name = "Devilry group"

    def ready(self):
        from django_cradmin.superuserui import superuserui_registry
        from devilry.devilry_group.views.download_files import backends
        appconfig = superuserui_registry.default.add_djangoapp(
                superuserui_registry.DjangoAppConfig(app_label='devilry_group'))
        appconfig.add_all_models()

        # add zip backend to registry
        backend_registry.Registry.get_instance().add(backends.DevilryGroupZipBackend)
