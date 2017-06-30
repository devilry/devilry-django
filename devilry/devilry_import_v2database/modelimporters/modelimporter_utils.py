import mimetypes

import sys
from django.conf import settings


class BulkCreator(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.max_bulk_create = getattr(settings,
                                       'DEVILRY_V2_DATABASE_MAX_BULK_CREATE_OVERRIDE',
                                       5000)
        self._objects = []

    def add(self, *obj):
        self._objects.extend(obj)
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


class ProgressDots(object):
    def __init__(self, interval=100, messageformat='One dot per {interval}: '):
        self._count = 0
        self._interval = interval
        self._messageformat = messageformat
        self._enabled = getattr(settings, 'DEVILRY_V2_DATABASE_PRINT_PROGRESS_DOTS', True)

    def increment_progress(self, increment=1):
        self._count += increment
        if self._enabled:
            if self._count % self._interval == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

    def __enter__(self):
        self._count = 0
        if self._enabled:
            sys.stdout.write(self._messageformat.format(interval=self._interval))
            sys.stdout.flush()
        return self

    def __exit__(self, ttype, value, traceback):
        if self._enabled:
            sys.stdout.write('\n')


def get_mimetype_from_filename(filename):
    mimetype = 'application/octet-stream'
    if filename:
        detected_mimetype = mimetypes.guess_type(filename)
        if detected_mimetype[0]:
            mimetype = detected_mimetype[0]
    return mimetype


def make_flat_v2_id(object_dict):
    return '{}__{}'.format(object_dict['model'].split('.')[1], object_dict['pk'])


def make_staticfeedback_fileattachment_v2_id(staticfeedback_id, attachment_id):
    return 'staticfeedbackfileattachment__{}__{}'.format(staticfeedback_id, attachment_id)
