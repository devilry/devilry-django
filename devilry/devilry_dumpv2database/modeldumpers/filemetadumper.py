import os

from devilry.apps.core.models import FileMeta
from devilry.devilry_dumpv2database import modeldumper


class FileMetaDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return FileMeta

    def serialize_model_object(self, obj):
        serialized = super(FileMetaDumper, self).serialize_model_object(obj=obj)
        file_path = obj.deliverystore._get_filepath(obj)
        root = obj.deliverystore.root
        relative_path = os.path.relpath(file_path, root)

        # settings.DEVILRY_FSHIERDELIVERYSTORE_ROOT
        serialized['fields']['relative_file_path'] = relative_path
        return serialized
