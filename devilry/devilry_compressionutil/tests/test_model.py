import os
import shutil
import io

import mock
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_compressionutil.models import pre_compressed_archive_meta_delete

# Dummy text for file
lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In facilisis dignissim enim eu luctus. ' \
              'Vivamus volutpat porta interdum. Curabitur porttitor justo ut turpis eleifend tristique. Cras posuere ' \
              'mauris vitae risus luctus, ac hendrerit mi rhoncus. Nullam ultricies mollis elit. Aenean venenatis, ' \
              'est at ultricies ullamcorper, velit neque ultrices sapien, vitae gravida orci odio a massa. Integer ' \
              'lobortis dapibus placerat. Nunc id odio id lacus dapibus iaculis. Praesent sit amet nibh faucibus, ' \
              'congue urna at, ornare risus. Quisque fringilla libero at metus interdum gravida. ' \
              'Quisque at pellentesque magna. Morbi sagittis magna in sollicitudin viverra. ' \
              'Donec quis velit suscipit, mollis leo ut.'


class TestCompressedFileMeta(TestCase):

    def setUp(self):
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')
        self.mock_registry = backend_registry.MockableRegistry.make_mockregistry(backend_mock.MockDevilryZipBackend)

    def tearDown(self):
        if os.path.exists(self.backend_path):
            shutil.rmtree(self.backend_path, ignore_errors=False)

    def __create_testfile(self):
        testfile = io.StringIO()
        testfile.write(lorem_ipsum)
        testfile.seek(0)
        return testfile

    def __setup_mock_backend(self, archive_path, file_size):
        mock_backend = self.mock_registry.get_instance().get(backend_mock.MockDevilryZipBackend.backend_id)(
            archive_path=archive_path, readmode=False)
        mock_backend.archive_size = mock.MagicMock(return_value=file_size)
        return mock_backend

    def __write_to_backend(self, backend, filename, file):
        backend.readmode = False
        backend.add_file(filename, file)
        backend.close()

    def test_manager_create_meta(self):
        # Does not create an actual file(we need to call backend.add_file for that.), but we are mocking
        # the data need from the backend to create a CompressedArchiveMeta entry.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                            self.mock_registry):
                testcomment = baker.make('devilry_group.GroupComment', user__shortname='user@example.com')
                archivepath = 'test.zip'
                mock_backend = self.mock_registry.get_instance().get(backend_mock.MockDevilryZipBackend.backend_id)(archive_path=archivepath)
                mock_backend.archive_size = mock.MagicMock(return_value=1)
                CompressedArchiveMeta.objects.create_meta(
                    instance=testcomment,
                    zipfile_backend=mock_backend,
                    user=baker.make(settings.AUTH_USER_MODEL))
                archive_meta = CompressedArchiveMeta.objects.get(content_object_id=testcomment.id)
                self.assertEqual(archive_meta.archive_path, os.path.join(self.backend_path, archivepath))

    def test_generic_foreignkey_comment(self):
        testcomment = baker.make('devilry_comment.Comment')
        archivemeta = baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertEqual(archivemeta.content_object_id, testcomment.id)
        self.assertEqual(type(archivemeta.content_object), type(testcomment))

    def test_archive_path_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            baker.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_archive_name_cannot_be_blank(self):
        with self.assertRaises(IntegrityError):
            baker.make('devilry_compressionutil.CompressedArchiveMeta', archive_path=None)

    def test_is_marked_for_delete_default_none(self):
        testcomment = baker.make('devilry_comment.Comment')
        archive_meta = baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        self.assertIsNone(archive_meta.deleted_datetime)

    def test_is_marked_for_delete_true(self):
        testcomment = baker.make('devilry_comment.Comment')
        archive_meta = baker.make('devilry_compressionutil.CompressedArchiveMeta',
                                  content_object=testcomment,
                                  deleted_datetime=timezone.now())
        self.assertTrue(archive_meta.deleted_datetime)

    def test_clean_invalid_backend_id(self):
        testcomment = baker.make('devilry_comment.Comment')
        archive_meta = baker.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
        with self.assertRaisesMessage(ValidationError, 'backend_id must refer to a valid backend'):
            archive_meta.full_clean()

    def test_compressed_archive_meta_delete_older_than_num_days(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                            self.mock_registry):
                archivepath1 = 'test1.zip'
                archivepath2 = 'test2.zip'

                # Create a testfile
                testfile_name = 'testfile.txt'
                testfile = self.__create_testfile()

                # Set up mock backend
                mock_backend1 = self.__setup_mock_backend(archive_path=archivepath1, file_size=testfile.tell())
                mock_backend2 = self.__setup_mock_backend(archive_path=archivepath2, file_size=testfile.tell())

                # Create archive meta
                compressed_archive_meta1 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend1,
                    user=baker.make(settings.AUTH_USER_MODEL))
                compressed_archive_meta2 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend2,
                    user=baker.make(settings.AUTH_USER_MODEL))

                compressed_archive_meta1.created_datetime = timezone.now()
                compressed_archive_meta2.created_datetime = timezone.now() - timezone.timedelta(days=10)
                compressed_archive_meta1.save()
                compressed_archive_meta2.save()

                # Write to backend
                self.__write_to_backend(backend=mock_backend1, filename='{}'.format(testfile_name), file=testfile)
                self.__write_to_backend(backend=mock_backend2, filename='{}'.format(testfile_name), file=testfile)

                compressed_archive_path1 = compressed_archive_meta1.archive_path
                compressed_archive_path2 = compressed_archive_meta2.archive_path
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertTrue(os.path.exists(compressed_archive_path2))

                CompressedArchiveMeta.objects.delete_compressed_archives_older_than(days=5)
                self.assertEqual(CompressedArchiveMeta.objects.count(), 1)
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertFalse(os.path.exists(compressed_archive_path2))

    def test_compressed_archive_meta_delete_older_than_num_seconds(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                            self.mock_registry):
                archivepath1 = 'test1.zip'
                archivepath2 = 'test2.zip'

                # Create a testfile
                testfile_name = 'testfile.txt'
                testfile = self.__create_testfile()

                # Set up mock backend
                mock_backend1 = self.__setup_mock_backend(archive_path=archivepath1, file_size=testfile.tell())
                mock_backend2 = self.__setup_mock_backend(archive_path=archivepath2, file_size=testfile.tell())

                # Create archive meta
                compressed_archive_meta1 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend1,
                    user=baker.make(settings.AUTH_USER_MODEL))
                compressed_archive_meta2 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend2,
                    user=baker.make(settings.AUTH_USER_MODEL))

                compressed_archive_meta1.created_datetime = timezone.now()
                compressed_archive_meta2.created_datetime = timezone.now() - timezone.timedelta(seconds=10)
                compressed_archive_meta1.save()
                compressed_archive_meta2.save()

                # Write to backend
                self.__write_to_backend(backend=mock_backend1, filename='{}'.format(testfile_name), file=testfile)
                self.__write_to_backend(backend=mock_backend2, filename='{}'.format(testfile_name), file=testfile)

                compressed_archive_path1 = compressed_archive_meta1.archive_path
                compressed_archive_path2 = compressed_archive_meta2.archive_path
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertTrue(os.path.exists(compressed_archive_path2))

                CompressedArchiveMeta.objects.delete_compressed_archives_older_than(seconds=5)
                self.assertEqual(CompressedArchiveMeta.objects.count(), 1)
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertFalse(os.path.exists(compressed_archive_path2))

    def test_compressed_archive_meta_delete_archives_marked_as_deleted(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                            self.mock_registry):
                archivepath1 = 'test1.zip'
                archivepath2 = 'test2.zip'

                # Create a testfile
                testfile_name = 'testfile.txt'
                testfile = self.__create_testfile()

                # Set up mock backend
                mock_backend1 = self.__setup_mock_backend(archive_path=archivepath1, file_size=testfile.tell())
                mock_backend2 = self.__setup_mock_backend(archive_path=archivepath2, file_size=testfile.tell())

                # Create archive meta
                compressed_archive_meta1 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend1,
                    user=baker.make(settings.AUTH_USER_MODEL))
                compressed_archive_meta2 = CompressedArchiveMeta.objects.create_meta(
                    instance=baker.make('devilry_group.GroupComment'),
                    zipfile_backend=mock_backend2,
                    user=baker.make(settings.AUTH_USER_MODEL))

                compressed_archive_meta1.created_datetime = timezone.now()
                compressed_archive_meta2.created_datetime = timezone.now()
                compressed_archive_meta2.deleted_datetime = timezone.now()
                compressed_archive_meta1.save()
                compressed_archive_meta2.save()

                # Write to backend
                self.__write_to_backend(backend=mock_backend1, filename='{}'.format(testfile_name), file=testfile)
                self.__write_to_backend(backend=mock_backend2, filename='{}'.format(testfile_name), file=testfile)

                compressed_archive_path1 = compressed_archive_meta1.archive_path
                compressed_archive_path2 = compressed_archive_meta2.archive_path
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertTrue(os.path.exists(compressed_archive_path2))

                CompressedArchiveMeta.objects.delete_compressed_archives_marked_as_deleted()
                self.assertEqual(CompressedArchiveMeta.objects.count(), 1)
                self.assertTrue(os.path.exists(compressed_archive_path1))
                self.assertFalse(os.path.exists(compressed_archive_path2))
