import shutil
import tempfile
import unittest

from django import test
from model_bakery import baker

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers import FileMetaImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
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

    def test_importer(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = baker.make('devilry_group.GroupComment')
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            self.assertEqual(CommentFile.objects.count(), 1)

    def test_importer_delivery_comment(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = baker.make('devilry_group.GroupComment')
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            group_comment = GroupComment.objects.get(id=comment_file.comment.id)
            self.assertEqual(group_comment, delivery_comment)

    def test_importer_filename(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = baker.make('devilry_group.GroupComment')
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.filename, 'test.py')

    def test_importer_mimetype(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = baker.make('devilry_group.GroupComment')
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.mimetype, 'text/x-python')
