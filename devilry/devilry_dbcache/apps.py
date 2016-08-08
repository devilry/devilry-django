from django.apps import AppConfig

from ievv_opensource.ievv_customsql import customsql_registry
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class DbCacheAppConfig(AppConfig):
    name = 'devilry.devilry_dbcache'
    verbose_name = "Database Cache"

    def ready(self):
        registry = customsql_registry.Registry.get_instance()
        registry.add('devilry_dbcache', AssignmentGroupDbCacheCustomSql)
