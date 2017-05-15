from devilry.devilry_import_v2database import v2dump_directoryparsers


class ModelImporterException(Exception):
    pass


class ModelImporter(object):
    def __init__(self, input_root):
        self.input_root = input_root

    def get_model_class(self):
        """
        Get the model class.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def target_model_has_objects(self):
        return self.get_model_class().objects.exists()

    def prettyformat_model_name(self):
        model_class = self.get_model_class()
        return '{}.{}'.format(model_class._meta.app_label,
                              model_class.__name__)

    def import_models(self):
        raise NotImplementedError()

    def patch_model_from_object_dict(self, model_object, object_dict, attributes):
        for attribute in attributes:
            if isinstance(attribute, tuple):
                from_attribute, to_attribute = attribute
            else:
                from_attribute = attribute
                to_attribute = attribute
            if from_attribute == 'pk':
                value = object_dict[from_attribute]
            else:
                value = object_dict['fields'][from_attribute]
            setattr(model_object, to_attribute, value)

    @property
    def v2user_directoryparser(self):
        return v2dump_directoryparsers.V2UserDirectoryParser(
            input_root=self.input_root)

    @property
    def v2subject_directoryparser(self):
        return v2dump_directoryparsers.V2SubjectDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2period_directoryparser(self):
        return v2dump_directoryparsers.V2PeriodDirectoryParser(
            input_root=self.input_root
        )
