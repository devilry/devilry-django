import tempfile
import json
import os
import shutil


class ImporterTestCaseMixin(object):

    def tearDown(self):
        shutil.rmtree(self.temp_root_dir)

    def create_v2dump(self, model_name, data):
        self.temp_root_dir = tempfile.mkdtemp()
        full_path_to_model_folder = os.path.join(self.temp_root_dir, model_name)
        os.makedirs(full_path_to_model_folder)
        # for key, value in data.iteritems():
        fp = open('{}/{}.json'.format(full_path_to_model_folder, data['pk']), 'w+')
        fp.write(json.dumps(data))
