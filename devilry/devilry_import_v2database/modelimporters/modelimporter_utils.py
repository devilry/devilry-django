from django.conf import settings

from devilry.devilry_import_v2database.models import ImportedModel


class BulkCreator(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.max_bulk_create = getattr(settings,
                                       'DEVILRY_V2_DATABASE_MAX_BULK_CREATE_OVERRIDE',
                                       5000)
        self._objects = []

    def add(self, obj):
        self._objects.append(obj)
        if len(self._objects) >= self.max_bulk_create:
            self.save_objects()

    def save_objects(self):
        if self._objects:
            self.model_class.objects.bulk_create(self._objects)
        self.clear()

    def clear(self):
        self._objects = []

    def __enter__(self):
        self.clear()
        # global logger_singleton
        # logger_singleton.save_objects()
        return self

    def __exit__(self, ttype, value, traceback):
        self.save_objects()


# logger_singleton = BulkCreator(model_class=ImportedModel)
