import json
import os

from django.core import serializers


class ModelDumper(object):
    def __init__(self, output_root):
        self.output_root = output_root

    def get_model_class(self):
        """
        Get the model class.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def prettyformat_model_name(self):
        model_class = self.get_model_class()
        return '{}.{}'.format(model_class._meta.app_label,
                              model_class.__name__)

    @property
    def output_directory(self):
        model_class = self.get_model_class()
        return os.path.join(
            self.output_root,
            '{}.{}'.format(model_class._meta.app_label,
                           model_class.__name__.lower()))

    def optimize_queryset(self, queryset):
        """
        Override this if you need to optimize the queryset
        (use select_related, prefetch_related, ...)
        """
        return queryset

    def get_object_iterator(self):
        return self.optimize_queryset(self.get_model_class().objects).iterator()

    def get_object_count(self):
        return self.get_model_class().objects.count()

    def serialize_model_object(self, obj):
        """
        Serialize a model object.
        """
        json_array = serializers.serialize('json', [obj], ensure_ascii=False)
        return json.loads(json_array[1:-1])

    def get_unique_id_for_model_object(self, obj):
        """
        Get the unique ID for the provided model object.

        Used to generate the output filename.

        Do not need to override this unless ``pk`` is not the unique ID.
        """
        return obj.pk

    def get_output_filepath_for_model_object(self, obj):
        filename = '{}.json'.format(self.get_unique_id_for_model_object(obj))
        return os.path.join(self.output_directory, filename)

    def serialize_all_objects_to_output_directory(self, fake=False):
        if not fake:
            if os.path.exists(self.output_directory):
                raise ValueError('The output_directory, {}, already exists. Aborting.'.format(
                    self.output_directory
                ))
            os.makedirs(self.output_directory)
        for obj in self.get_object_iterator():
            serialized = self.serialize_model_object(obj)
            filepath = self.get_output_filepath_for_model_object(obj)
            if fake:
                print
                print '##', filepath
                print serialized
                print
            else:
                with open(filepath, 'wb') as outfile:
                    outfile.write(json.dumps(serialized, encoding='utf-8', indent=2))
                    outfile.close()
