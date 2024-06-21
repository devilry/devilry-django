# Python imports
import io
import os
import pathlib
import posixpath
import shutil

# Django imports

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.base import ContentFile

# Devilry imports
from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock

# Dummy text for compression tests
lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In facilisis dignissim enim eu luctus. ' \
              'Vivamus volutpat porta interdum. Curabitur porttitor justo ut turpis eleifend tristique. Cras posuere ' \
              'mauris vitae risus luctus, ac hendrerit mi rhoncus. Nullam ultricies mollis elit. Aenean venenatis, ' \
              'est at ultricies ullamcorper, velit neque ultrices sapien, vitae gravida orci odio a massa. Integer ' \
              'lobortis dapibus placerat. Nunc id odio id lacus dapibus iaculis. Praesent sit amet nibh faucibus, ' \
              'congue urna at, ornare risus. Quisque fringilla libero at metus interdum gravida. ' \
              'Quisque at pellentesque magna. Morbi sagittis magna in sollicitudin viverra. ' \
              'Donec quis velit suscipit, mollis leo ut.'


@override_settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY='devilry_compressed_archives')
class TestZipBackend(TestCase):

    def setUp(self):
        # Set up a backend path for testing which can be removed after each test.
        self.backend_path = pathlib.Path('devilry_testfiles') / 'devilry_compressed_archives'

    def tearDown(self):
        if self.backend_path.exists():
            shutil.rmtree(self.backend_path.absolute(), ignore_errors=False)

    def test_path_without_tar_extension(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='testpath')
        self.assertEqual('testpath.tar.gz', backend.archive_path)
        self.assertEqual(
            posixpath.join(settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY, 'testpath.tar.gz'),
            backend.archive_full_path)

    def test_path_with_tar_extension(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='testpath.tar.gz')
        self.assertEqual('testpath.tar.gz', backend.archive_path)

    def test_open_archive_is_none(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='testpath')
        with self.assertRaises(FileNotFoundError):
            backend.read_archive()

    def test_open_readmode_false(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='testpath', readmode=False)
        with self.assertRaisesMessage(ValueError, 'Must be in readmode'):
            backend.read_archive()

    def test_add_file_readmode_true(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='testpath')
        with self.assertRaisesMessage(
                ValueError, 'readmode must be False to add files.'):
            backend.add_file('', None)

    def test_close_archive_is_none(self):
        testpath = 'testpath'
        backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
        backend.close()

    def test_size_archive_none(self):
        testpath = 'testpath'
        backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
        with self.assertRaises(FileNotFoundError):
            backend.archive_size()

    def test_is_compressed(self):
        # Simply checks that the compressed archives size is less than the file written to it.
        mockregistry = backend_registry.MockableRegistry.make_mockregistry(
            backend_mock.MockDevilryZipBackend
        )
        # Get backend and set storage path
        backend_class = mockregistry.get('default')
        backend = backend_class(archive_path='testfile', readmode=False)

        # Create testfile
        filename = 'testfile.txt'
        testfile = ContentFile(lorem_ipsum.encode('utf-8'))

        # Write to backend
        backend.add_file(filename, testfile)
        backend.close()

        # Read from created archive
        backend.readmode = True
        self.assertTrue(backend.archive_size() < testfile.tell())

    def test_add_file(self):
        # Add file to archive
        mockregistry = backend_registry.MockableRegistry.make_mockregistry(
            backend_mock.MockDevilryZipBackend
        )
        # Get backend and set storage path
        backend_class = mockregistry.get('default')
        backend = backend_class(archive_path='testfile1', readmode=False)

        # Create testfile
        testfile = ContentFile(b'testcontent')

        # Write to backend
        backend.add_file('testfile.txt', testfile)
        backend.close()

        # Read from created archive
        backend.readmode = True
        archive = backend.read_archive()
        self.assertEqual(b'testcontent', archive.extractfile(archive.getmembers()[0]).read())

    def test_read_archive(self):
        # Reads archive and checks that content is as expected.
        mockregistry = backend_registry.MockableRegistry.make_mockregistry(
            backend_mock.MockDevilryZipBackend
        )
        # Get backend and set storage path
        backend_class = mockregistry.get('default')
        backend = backend_class(archive_path='testfile', readmode=False)

        # Create testfile
        testfile = ContentFile(b'testcontent')

        # Write to backend
        backend.add_file('{}'.format('testfile1.txt'), testfile)
        testfile.seek(0)
        backend.add_file('{}'.format('testfile2.txt'), testfile)
        backend.close()

        # Read from created archive
        backend.readmode = True
        archive = backend.read_archive()
        self.assertEqual(b'testcontent', archive.extractfile(archive.getmembers()[0]).read())
        self.assertEqual(b'testcontent', archive.extractfile(archive.getmembers()[1]).read())

    def test_deep_nesting(self):
        # Tests deep nesting of folders.
        nesting_levels = [
            os.path.join('dir1', 'testfile.txt'),
            os.path.join('dir1', 'dir1_dir1', 'testfile.txt'),
            os.path.join('dir1', 'dir1_dir2', 'testfile.txt'),
            os.path.join('dir2', 'dir2_dir1', 'testfile.txt')
        ]

        mockregistry = backend_registry.MockableRegistry.make_mockregistry(
            backend_mock.MockDevilryZipBackend
        )
        # Get backend and set storage path
        backend_class = mockregistry.get('default')
        backend = backend_class(archive_path='testfile1', readmode=False)

        # Create testfile
        testfile = ContentFile(b'testcontent')

        # Write to backend
        backend.add_file(os.path.join('dir1', 'testfile.txt'), testfile)
        testfile.seek(0)
        backend.add_file(os.path.join('dir1', 'dir1_dir1', 'testfile.txt'), testfile)
        testfile.seek(0)
        backend.add_file(os.path.join('dir2', 'dir2_dir1', 'testfile.txt'), testfile)
        testfile.seek(0)
        backend.add_file(os.path.join('dir1', 'dir1_dir2', 'testfile.txt'), testfile)
        backend.close()

        backend.readmode = True
        archive = backend_class(archive_path='testfile1', readmode=True).read_archive()
        for item in archive.getnames():
            self.assertTrue(item in nesting_levels)
