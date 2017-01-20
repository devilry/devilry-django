import os
import shutil

import mock
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_compressionutil.models import pre_compressed_archive_meta_delete


class TestCompressedFileMeta(TestCase):

    def setUp(self):
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')
        self.mock_registry = backend_registry.MockableRegistry.make_mockregistry(backend_mock.MockDevilryZipBackend)

    def tearDown(self):
        if os.path.exists(self.backend_path):
            shutil.rmtree(self.backend_path, ignore_errors=False)

    def test_manager_create_meta(self):
        # Does not create an actual file(we need to call backend.add_file for that.), but we are mocking
        # the data need from the backend to create a CompressedArchiveMeta entry.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                            self.mock_registry):
                testcomment = mommy.make('devilry_group.GroupComment', user__shortname='user@example.com')
                archivepath = 'test.zip'
                mock_backend = self.mock_registry.get_instance().get(backend_mock.MockDevilryZipBackend.backend_id)(archive_path=archivepath)
                mock_backend.archive_size = mock.MagicMock(return_value=1)
                CompressedArchiveMeta.objects.create_meta(
                    instance=testcomment,
                    zipfile_backend=mock_backend)
                archive_meta = CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
                self.assertEquals(archive_meta.archive_path, os.path.join(self.backend_path, archivepath))

    def test_generic_foreignkey_comment(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archivemeta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertEquals(archivemeta.content_object_id, testcomment.id)
        self.assertEquals(type(archivemeta.content_object), type(testcomment))

    def test_archive_path_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_archive_name_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_is_marked_for_delete_default_none(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertIsNone(archive_meta.deleted_datetime)

    def test_is_marked_for_delete_true(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                                  content_object=testcomment,
                                  deleted_datetime=timezone.now())
        self.assertTrue(archive_meta.deleted_datetime)

    def test_clean_invalid_backend_id(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        with self.assertRaisesMessage(ValidationError, 'backend_id must refer to a valid backend'):
            archive_meta.full_clean()

    # def test_precompressed_archive_meta_delete(self):
    #     from devilry.devilry_group import devilry_group_mommy_factories
    #     from devilry.devilry_dbcache import customsql
    #     from ievv_opensource.ievv_batchframework import batchregistry
    #     from devilry.devilry_group import tasks
    #     customsql.AssignmentGroupDbCacheCustomSql().initialize()
    #     with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
    #         with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
    #                         self.mock_registry):
    #             # testcomment = mommy.make('devilry_group.GroupComment', user__shortname='user@example.com')
    #             testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished()
    #             archivepath = 'test.zip'
    #             mock_backend = self.mock_registry.get_instance().get(backend_mock.MockDevilryZipBackend.backend_id)(
    #                 archive_path=archivepath)
    #             mock_backend.archive_size = mock.MagicMock(return_value=1)
    #             archive_meta = CompressedArchiveMeta.objects.create_meta(
    #                 instance=testfeedbackset,
    #                 zipfile_backend=mock_backend)
    #
    #             testcomment = mommy.make('devilry_group.GroupComment',
    #                                      feedback_set=testfeedbackset,
    #                                      user_role='student',
    #                                      user__shortname='testuser@example.com')
    #             commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
    #             commentfile.file.save('testfile.txt', ContentFile('testcontent'))
    #
    #             batchregistry.Registry.get_instance().add_actiongroup(
    #                 batchregistry.ActionGroup(
    #                     name='batchframework_feedbackset',
    #                     mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
    #                     actions=[
    #                         tasks.FeedbackSetCompressAction
    #                     ]))
    #             batchregistry.Registry.get_instance().run(
    #                 actiongroup_name='batchframework_feedbackset',
    #                 context_object=testfeedbackset,
    #                 test='test')
    #             CompressedArchiveMeta.objects.get(id=archive_meta.id).delete()
    #             with self.assertRaises(CompressedArchiveMeta.DoesNotExist):
    #                 CompressedArchiveMeta.objects.get(id=archive_meta.id)
