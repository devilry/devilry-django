import os
import shutil
import tempfile
import unittest

from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers import CommentFileContentImporter, \
    FileMetaImporter, StaticFeedbackImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestCommentFileContentImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        self.v2_delivery_root_temp_dir = tempfile.mkdtemp()
        self.v2_feedback_root_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestCommentFileContentImporter, self).tearDown()
        shutil.rmtree('devilry_testfiles', ignore_errors=True)
        shutil.rmtree(self.v2_delivery_root_temp_dir)
        shutil.rmtree(self.v2_feedback_root_temp_dir)

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

    def test_filemeta_missing_file_root_setting(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=None):
            delivery_comment = baker.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write(b'import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            CommentFileContentImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.file.name, '')

    def test_filemeta_filecontent(self):
        with self.settings(DEVILRY_V2_DELIVERY_FILE_ROOT=self.v2_delivery_root_temp_dir):
            delivery_comment = baker.make('devilry_group.GroupComment')
            v2_file = open(os.path.join(self.v2_delivery_root_temp_dir, 'test.py'), 'wb')
            v2_file.write(b'import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.filemeta',
                data=self._create_filemeta_dict(delivery_comment, 'test.py')
            )
            FileMetaImporter(input_root=self.temp_root_dir).import_models()
            CommentFileContentImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.file.read(), b'import os')
            self.assertEqual(comment_file.filesize, 9)

    def _create_staticfeedback_dict(self, files):
        return {
            'pk': 1,
            'model': 'core.staticfeedback',
            'fields': {
                'is_passing_grade': True,
                'grade': '2/4',
                'saved_by': baker.make(settings.AUTH_USER_MODEL).id,
                'delivery': 1,
                'points': 2,
                'files': files,
                'deadline_id': baker.make('devilry_group.FeedbackSet').id,
                'save_timestamp': '2017-05-15T11:04:46.817',
                'rendered_view': 'test'
            }
        }

    def test_staticfeedbackattachment_missing_file_root_setting(self):
        with self.settings(DEVILRY_V2_MEDIA_ROOT=None):
            v2_file = open(os.path.join(self.v2_feedback_root_temp_dir, 'test.py'), 'wb')
            v2_file.write(b'import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.staticfeedback',
                data=self._create_staticfeedback_dict(
                    files={
                        '1': {
                            'id': 1,
                            'filename': 'test.py',
                            'relative_file_path': 'test.py',
                        },
                    })
            )
            StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
            CommentFileContentImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.file.name, '')

    def test_staticfeedbackattachment_filecontent(self):
        with self.settings(DEVILRY_V2_MEDIA_ROOT=self.v2_feedback_root_temp_dir):
            v2_file = open(os.path.join(self.v2_feedback_root_temp_dir, 'test.py'), 'wb')
            v2_file.write(b'import os')
            v2_file.close()
            self.create_v2dump(
                model_name='core.staticfeedback',
                data=self._create_staticfeedback_dict(
                    files={
                        '1': {
                            'id': 1,
                            'filename': 'test.py',
                            'relative_file_path': 'test.py',
                        },
                    })
            )
            StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
            CommentFileContentImporter(input_root=self.temp_root_dir).import_models()
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.file.read(), b'import os')
            self.assertEqual(comment_file.filesize, 9)
