import json
import os

from django.db import connection


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

    @property
    def meta_file_for_model(self):
        """
        """
        return '{}.{}.json'.format(self.get_app_label(), self.get_model_name_lowercase())

    def get_model_class_meta_dict(self):
        """
        """
        file_path = os.path.join(self.input_root, self.meta_file_for_model)
        if not os.path.isfile(file_path):
            return None
        with open(file_path, 'rb') as file_object:
            file_content = file_object.read()
            return json.loads(file_content.decode('utf-8'))

    def set_max_id_for_models_with_auto_generated_sequence_numbers(self, model_class):
        """
        """
        meta_dict = self.get_model_class_meta_dict()
        if not meta_dict:
            return
        sql = """
        SELECT setval(pg_get_serial_sequence('{db_table}', 'id'), {max_id});
        """.format(db_table=model_class._meta.db_table, max_id=meta_dict['max_id'])
        cursor = connection.cursor()
        cursor.execute(sql)

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
