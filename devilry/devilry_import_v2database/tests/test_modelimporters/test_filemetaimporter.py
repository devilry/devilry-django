from django import test

import os
import shutil

from devilry.devilry_comment.models import CommentFile

from model_mommy import mommy

from devilry.devilry_group.models import GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers import FileMetaImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestFileMetaImporter(ImporterTestCaseMixin, test.TestCase):
    def tearDown(self):
        super(TestFileMetaImporter, self).tearDown()
        shutil.rmtree('devilry_testfiles', ignore_errors=True)

    def _create_filemeta_dict(self, delivery_comment, file_path):
        return {
            'pk': 580,
            'model': 'core.filemeta',
            'fields': {
                'delivery': delivery_comment.id,
                'absolute_file_path': file_path,
                'filename': 'test.py',
                'mimetype': 'text/x-python',
                'size': 12
            }
        }

    def test_importer(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(CommentFile.objects.count(), 1)
        os.remove(abs_path)

    def test_importer_delivery_comment(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        comment_file = CommentFile.objects.first()
        group_comment = GroupComment.objects.get(id=comment_file.comment.id)
        self.assertEquals(group_comment, delivery_comment)
        os.remove(abs_path)

    def test_importer_size(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        comment_file = CommentFile.objects.first()
        self.assertEquals(comment_file.filesize, 12)
        os.remove(abs_path)

    def test_importer_filename(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        comment_file = CommentFile.objects.first()
        self.assertEquals(comment_file.filename, 'test.py')
        os.remove(abs_path)

    def test_importer_mimetype(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        comment_file = CommentFile.objects.first()
        self.assertEquals(comment_file.mimetype, 'text/x-python')
        os.remove(abs_path)

    def test_importer_file_content(self):
        delivery_comment = mommy.make('devilry_group.GroupComment')
        v2_file = open('test.py', 'wb')
        v2_file.write('import os')
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        self.create_v2dump(
            model_name='core.filemeta',
            data=self._create_filemeta_dict(delivery_comment, abs_path)
        )
        FileMetaImporter(input_root=self.temp_root_dir).import_models()
        comment_file = CommentFile.objects.first()
        self.assertEquals(comment_file.file.read(), 'import os')
        os.remove(abs_path)
