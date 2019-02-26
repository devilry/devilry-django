import tempfile
import json
import os
import shutil


class ImporterTestCaseMixin(object):

    def tearDown(self):
        shutil.rmtree(self.temp_root_dir)

    def create_v2dump(self, model_name, data, model_meta=None):
        self.temp_root_dir = tempfile.mkdtemp()
        full_path_to_model_folder = os.path.join(self.temp_root_dir, model_name)
        os.makedirs(full_path_to_model_folder)
        # for key, value in data.iteritems():
        if model_meta:
            meta_out_file = open('{}/{}.json'.format(self.temp_root_dir, model_name), 'wb')
            meta_out_file.write(json.dumps(model_meta).encode('utf-8'))
            meta_out_file.close()
        fp = open('{}/{}.json'.format(full_path_to_model_folder, data['pk']), 'w+')
        fp.write(json.dumps(data))
        fp.close