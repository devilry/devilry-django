import os

import mock
import shutil

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from model_mommy import mommy

from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_compressionutil.backends.backend_mock import MockDevilryZipBackend
from devilry.devilry_compressionutil import backend_registry


class TestCompressedFileMeta(TestCase):

    def setUp(self):
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        if os.path.exists(self.backend_path):
            shutil.rmtree(self.backend_path, ignore_errors=False)

    def test_manager_create_meta(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testcomment = mommy.make('devilry_group.GroupComment', user__shortname='user@example.com')
            archivepath = 'test.zip'
            backend_registry.Registry.get_instance().add(MockDevilryZipBackend)
            mock_backend_class = backend_registry.Registry.get_instance().get(MockDevilryZipBackend.backend_id)
            mock_backend = mock_backend_class(archive_path=archivepath)
            mock_backend.archive_size = mock.MagicMock(return_value=1)
            CompressedArchiveMeta.objects.create_meta(instance=testcomment, zipfile_backend=mock_backend)
            archive_meta = CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
            self.assertEquals(archive_meta.archive_path, os.path.join(self.backend_path, archivepath))

    def test_generic_foreignkey_comment(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archivemeta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertEquals(archivemeta.content_object_id, testcomment.id)
        self.assertEquals(type(archivemeta.content_object), type(testcomment))

    def test_unique_constraint(self):
        testcomment = mommy.make('devilry_comment.Comment')
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)

        with self.assertRaises(IntegrityError):
            mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)

    def test_archive_path_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_archive_name_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_is_marked_for_delete_default_none(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertIsNone(archive_meta.delete)

    def test_is_marked_for_delete_true(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment, delete=True)
        self.assertTrue(archive_meta.delete)

    def test_clean_invalid_backend_id(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        with self.assertRaisesMessage(ValidationError, 'backend_id must refer to a valid backend'):
            archive_meta.full_clean()
