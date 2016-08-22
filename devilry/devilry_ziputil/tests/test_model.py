import mock

from django.db import IntegrityError
from django.test import TestCase
from model_mommy import mommy

from devilry.devilry_ziputil.models import CompressedArchiveMeta
from devilry.devilry_ziputil.backends.backend_mock import MockDevilryZipBackend


class TestCompressedFileMeta(TestCase):

    def test_manager_create_meta(self):
        archivepath = 'path/test.zip'
        testcomment = mommy.make('devilry_group.GroupComment', user__shortname='user@example.com')
        mock_backend = MockDevilryZipBackend(
                dry_run=True,
                archive_path=archivepath)
        mock_backend.archive_size = mock.MagicMock(return_value=1)
        CompressedArchiveMeta.objects.create_meta(instance=testcomment, zipfile_backend=mock_backend)
        archive_meta = CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
        self.assertEquals(archive_meta.archive_path, '{}{}'.format(mock_backend.get_storage_location(), archivepath))

    def test_generic_foreignkey_comment(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archivemeta = mommy.make('devilry_ziputil.CompressedArchiveMeta', content_object=testcomment)
        self.assertEquals(archivemeta.content_object_id, testcomment.id)
        self.assertEquals(type(archivemeta.content_object), type(testcomment))

    def test_unique_constraint(self):
        testcomment = mommy.make('devilry_comment.Comment')
        mommy.make('devilry_ziputil.CompressedArchiveMeta', content_object=testcomment)

        with self.assertRaises(IntegrityError):
            mommy.make('devilry_ziputil.CompressedArchiveMeta', content_object=testcomment)

    def test_archive_path_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_ziputil.CompressedArchiveMeta', archive_path=None)

    def test_archive_name_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_ziputil.CompressedArchiveMeta', archive_path=None)
