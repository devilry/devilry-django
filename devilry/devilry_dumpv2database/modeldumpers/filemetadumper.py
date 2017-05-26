from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import FileMeta
import os
import mimetypes


class FileMetaDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return FileMeta

    def serialize_model_object(self, obj):
        serialized = super(FileMetaDumper, self).serialize_model_object(obj=obj)
        file_abs_path = os.path.abspath(obj.deliverystore._get_filepath(obj))
        serialized['fields']['absolute_file_path'] = file_abs_path
        serialized['fields']['mimetype'] = mimetypes.guess_type(obj.filename)[0]
        return serialized
