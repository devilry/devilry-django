# Python imports
import io
import os
import shutil
import zipfile

# Django imports
from unittest import skip

from django.test import TestCase
from django.conf import settings

# Devilry imports
from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock
from devilry.devilry_compressionutil.backends.backends_base import PythonTarFileBackend

# Dummy text for compression tests
lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In facilisis dignissim enim eu luctus. ' \
              'Vivamus volutpat porta interdum. Curabitur porttitor justo ut turpis eleifend tristique. Cras posuere ' \
              'mauris vitae risus luctus, ac hendrerit mi rhoncus. Nullam ultricies mollis elit. Aenean venenatis, ' \
              'est at ultricies ullamcorper, velit neque ultrices sapien, vitae gravida orci odio a massa. Integer ' \
              'lobortis dapibus placerat. Nunc id odio id lacus dapibus iaculis. Praesent sit amet nibh faucibus, ' \
              'congue urna at, ornare risus. Quisque fringilla libero at metus interdum gravida. ' \
              'Quisque at pellentesque magna. Morbi sagittis magna in sollicitudin viverra. ' \
              'Donec quis velit suscipit, mollis leo ut.'

class TestStreamZipBackend(TestCase):

    def setUp(self):
        # Set up a backend path for testing which can be removed after each test.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        shutil.rmtree(self.backend_path, ignore_errors=False)

    def _create_test_file(self, content=b'testcontent'):
        testfile = io.BytesIO()
        testfile.write(content)
        testfile.seek(0)

        return testfile

    def test_add_file(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                backend_mock.MockDevilryStreamZipBackend
            )

            backend_class = mockregistry.get('stream')
            backend = backend_class(archive_path='testfile1', readmode=False)

            file_1 = self._create_test_file()

            backend.add_file('testfile.txt', file_1)
            self.assertEqual(backend.files[0], ('testfile.txt', file_1))

            backend.close()

            archive = backend.read_archive()
            self.assertEqual(b'testcontent', archive.read(archive.namelist()[0]))


class TestZipBackend(TestCase):

    def setUp(self):
        # Set up a backend path for testing which can be removed after each test.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        shutil.rmtree(self.backend_path, ignore_errors=False)

    def test_path_without_zip_extension(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            self.assertEqual(settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip', backend.archive_path)

    def test_path_with_zip_extension(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            self.assertNotEqual(
                    settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip.zip',
                    backend.archive_path)
            self.assertEqual(
                    settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip',
                    backend.archive_path)

    def test_open_archive_is_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.read_archive()

    def test_open_readmode_false(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            backend = backend_mock.MockDevilryZipBackend(archive_path='testpath', readmode=False)
            with self.assertRaisesMessage(ValueError, 'Must be in readmode'):
                backend.read_archive()

    def test_open_readmode_true(self):
        # Raises ValueError since the archive is None. This is just to test that the readmode
        # error doesnt kick in.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath, readmode=False)
            backend.readmode = True
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.read_archive()

    def test_add_file_readmode_true(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            backend = backend_mock.MockDevilryZipBackend(archive_path='testpath')
            with self.assertRaisesMessage(ValueError, 'readmode must be False to add files.'):
                backend.add_file('', None)

    def test_close_archive_is_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.close()

    def test_size_archive_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.archive_size()

    def test_is_compressed(self):
        # Simply checks that the compressed archives size is less than the file written to it.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                backend = backend_class(archive_path='testfile', readmode=False)

                # Create testfile
                filename = 'testfile.txt'
                testfile = io.StringIO()
                testfile.write(lorem_ipsum)
                testfile.seek(0)

                # Write to backend
                backend.add_file('{}'.format(filename), testfile)
                backend.close()

                # Read from created archive
                backend.readmode = True
                self.assertTrue(backend.archive_size() < testfile.tell())

    def test_add_file(self):
            # Add file to archive
            with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                backend = backend_class(archive_path='testfile1', readmode=False)

                # Create testfile
                testfile = io.StringIO()
                testfile.write('testcontent')
                testfile.seek(0)

                # Write to backend
                backend.add_file('testfile.txt', testfile)
                backend.close()

                # Read from created archive
                backend.readmode = True
                archive = backend.read_archive()
                self.assertEqual(b'testcontent', archive.read(archive.namelist()[0]))

    def test_read_archive(self):
            # Reads archive and checks that content is as expected.
            with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                backend = backend_class(archive_path='testfile', readmode=False)

                # Create testfile
                testfile = io.StringIO()
                testfile.write('testcontent')
                testfile.seek(0)

                # Write to backend
                backend.add_file('{}'.format('testfile1.txt'), testfile)
                testfile.seek(0)
                backend.add_file('{}'.format('testfile2.txt'), testfile)
                backend.close()

                # Read from created archive
                backend.readmode = True
                archive = backend.read_archive()
                self.assertEqual(b'testcontent', archive.read(archive.namelist()[0]))
                self.assertEqual(b'testcontent', archive.read(archive.namelist()[1]))

    def test_deep_nesting(self):
        # Tests deep nesting of folders.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
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
            testfile = io.StringIO()
            testfile.write('testcontent')
            testfile.seek(0)

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
            for item in backend.archive.namelist():
                self.assertTrue(item in nesting_levels)


@skip('Skip tarfile tests until tarfile is complete(possible goal 3.1)')
class TestTarFileBackend(TestCase):

    def setUp(self):
        # Set up a backend path for testing which can be removed after each test.
        self.backend_path = os.path.join('devilry_testfiles', 'devilry_compressed_archives', '')

    def tearDown(self):
        shutil.rmtree(self.backend_path, ignore_errors=False)

    def test_add_file(self):
        backend = PythonTarFileBackend(archive_path='test', archive_name='test', compression='')
        backend.readmode = False

        testfile = io.StringIO()
        testfile.write('testcontent')
        testfile.seek(0)

        backend.add_file('testfile.txt', testfile)
        backend.close()

    def test_deep_nesting(self):
        nesting_levels = [
            os.path.join('test'),
            os.path.join('test', 'dir1'),
            os.path.join('test', 'dir2'),

            os.path.join('test', 'dir1', 'dir1_dir1'),
            os.path.join('test', 'dir1', 'dir1_dir2'),
            os.path.join('test', 'dir1', 'dir1_dir1', 'testfile.txt'),
            os.path.join('test', 'dir1', 'dir1_dir2', 'testfile.txt'),

            os.path.join('test', 'dir2', 'dir2_dir1'),
            os.path.join('test', 'dir2', 'dir2_dir1', 'testfile.txt'),
        ]

        backend = PythonTarFileBackend(archive_path='test', archive_name='test', compression='')
        backend.readmode = False

        testfile = io.StringIO()
        testfile.write('testcontent')
        testfile.seek(0)

        backend.add_file(os.path.join('dir1', 'dir1_dir1', 'testfile.txt'), testfile)
        testfile.seek(0)
        backend.add_file(os.path.join('dir2', 'dir2_dir1', 'testfile.txt'), testfile)
        testfile.seek(0)
        backend.add_file(os.path.join('dir1', 'dir1_dir2', 'testfile.txt'), testfile)
        backend.close()

        backend.readmode = True
        archive = backend.read_archive()

        for member in archive.getmembers():
            self.assertTrue(member.name in nesting_levels)

    def test_uncompressed_size(self):
        backend_uncompressed = PythonTarFileBackend(
                archive_path='test_uncompressed',
                archive_name='test_uncompressed',
                compression='')
        backend_uncompressed.readmode = False

        backend_gz = PythonTarFileBackend(
                archive_path='test_gz',
                archive_name='test_gz',
                compression='gz')
        backend_gz.readmode = False

        testfile = io.StringIO()
        testfile.write(lorem_ipsum)
        testfile.seek(0)

        backend_uncompressed.add_file('testfile_uncompressed.txt', testfile)
        backend_uncompressed.close()

        testfile.seek(0)

        backend_gz.add_file('testfile_gz_compressed.txt', testfile)
        backend_gz.close()

        backend_uncompressed.readmode = True
        backend_gz.readmode = True

        self.assertTrue(backend_uncompressed.archive_size() > backend_gz.archive_size())

    def test_gzip_size(self):
        backend_uncompressed = PythonTarFileBackend(
                archive_path='test_uncompressed',
                archive_name='test_uncompressed',
                compression='')
        backend_uncompressed.readmode = False

        backend_gz = PythonTarFileBackend(
                archive_path='test_gz',
                archive_name='test_gz',
                compression='gz')
        backend_gz.readmode = False

        testfile = io.StringIO()
        testfile.write(lorem_ipsum)
        testfile.seek(0)

        backend_uncompressed.add_file('testfile_uncompressed', testfile)
        backend_uncompressed.close()

        testfile.seek(0)

        backend_gz.add_file('testfile_gz_compressed.txt', testfile)
        backend_gz.close()

        backend_uncompressed.readmode = True
        backend_gz.readmode = True

        self.assertTrue(backend_gz.archive_size() < backend_uncompressed.archive_size())

    def test_bzip2_size(self):
        backend_uncompressed = PythonTarFileBackend(
                archive_path='test_uncompressed',
                archive_name='test_uncompressed',
                compression='')
        backend_uncompressed.readmode = False

        backend_bz2 = PythonTarFileBackend(
                archive_path='test_gz',
                archive_name='test_gz',
                compression='bz2')
        backend_bz2.readmode = False

        testfile = io.StringIO()
        testfile.write(lorem_ipsum)
        testfile.seek(0)

        backend_uncompressed.add_file('testfile_uncompressed.txt', testfile)
        backend_uncompressed.close()

        testfile.seek(0)

        backend_bz2.add_file('testfile_gz_compressed.txt', testfile)
        backend_bz2.close()

        backend_uncompressed.readmode = True
        backend_bz2.readmode = True

        self.assertTrue(backend_bz2.archive_size() < backend_uncompressed.archive_size())
