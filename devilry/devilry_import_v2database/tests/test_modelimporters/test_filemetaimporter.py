import os
import shutil
import tempfile

from django import test
from model_mommy import mommy

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers import FileMetaImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestFileMetaImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        self.v2_delivery_root_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestFileMetaImporter, self).tearDown()
        shutil.rmtree('devilry_testfiles', ignore_errors=True)
        shutil.rmtree(self.v2_delivery_root_temp_dir)

    def _create_filemeta_dict(self, delivery_comment, relative_file_path):
        return {
            'pk': 580,
            'model': 'core.filemeta',
            'fields': {
                'delivery': delivery_comment.id,
                'relative_file_path': relative_file_path,
                'filename': 'test.py',
                'mimetype': 'text/x-python',
                'size': 12
            }
        }

    def test_missing_file_root_setting(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=None):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            self.assertEquals(CommentFile.objects.count(), 0)

    def test_importer(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            self.assertEquals(CommentFile.objects.count(), 1)

    def test_importer_delivery_comment(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            group_comment = GroupComment.objects.get(id=comment_file.comment.id)
            self.assertEquals(group_comment, delivery_comment)

    def test_importer_size(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEquals(comment_file.filesize, 12)

    def test_importer_filename(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEquals(comment_file.filename, 'test.py')

    def test_importer_mimetype(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEquals(comment_file.mimetype, 'text/x-python')

    def test_importer_file_content(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = mommy.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write('import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEquals(comment_file.file.read(), 'import os')