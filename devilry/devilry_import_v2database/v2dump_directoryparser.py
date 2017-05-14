import json
import os


class V2DumpDirectoryParser(object):
    def __init__(self, input_root):
        self.input_root = input_root

    def get_app_label(self):
        """
        Get the app label of the model in v2.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def get_model_name_lowercase(self):
        """
        Get the lowercase model name in v2.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def prettyformat_v2_model_name(self):
        return '{}.{}'.format(self.get_app_label(),
                              self.get_model_name_lowercase())

    @property
    def input_directory(self):
        return os.path.join(
            self.input_root,
            '{}.{}'.format(self.get_app_label(),
                           self.get_model_name_lowercase()))

    def get_object_dict_by_filename(self, filename):
        filepath = os.path.join(self.input_directory, filename)
        with open(filepath, 'rb') as fileobject:
            filecontent = fileobject.read()
            return json.loads(filecontent.decode('utf-8'))

    def get_filename_from_id(self, id):
        return os.path.join(self.input_directory, '{}.json'.format(id))

    def get_object_dict_by_id(self, id):
        filename = self.get_filename_from_id(id)
        return self.get_object_dict_by_filename(filename)

    def iterate_object_dicts(self):
        for filename in os.listdir(self.input_directory):
            if filename.endswith('.json'):
                yield self.get_object_dict_by_filename(filename)
