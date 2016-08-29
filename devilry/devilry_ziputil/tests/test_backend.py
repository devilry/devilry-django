# Python imports
import os
import shutil

# Django imports
from django.test import TestCase
from django.conf import settings

# Devilry imports
from devilry.devilry_ziputil import backend_registry
from devilry.devilry_ziputil.backends import backend_mock

# Dummy text for compression tests
lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In facilisis dignissim enim eu luctus. ' \
              'Vivamus volutpat porta interdum. Curabitur porttitor justo ut turpis eleifend tristique. Cras posuere ' \
              'mauris vitae risus luctus, ac hendrerit mi rhoncus. Nullam ultricies mollis elit. Aenean venenatis, ' \
              'est at ultricies ullamcorper, velit neque ultrices sapien, vitae gravida orci odio a massa. Integer ' \
              'lobortis dapibus placerat. Nunc id odio id lacus dapibus iaculis. Praesent sit amet nibh faucibus, ' \
              'congue urna at, ornare risus. Quisque fringilla libero at metus interdum gravida. ' \
              'Quisque at pellentesque magna. Morbi sagittis magna in sollicitudin viverra. ' \
              'Donec quis velit suscipit, mollis leo ut.'


class TestZipBackend(TestCase):

    def setUp(self):
        # Set up a backend path for testing which can be removed after each test.
        self.backend_path = 'devilry_testfiles/devilry_compressed_archives/'

    def tearDown(self):
        shutil.rmtree(self.backend_path, ignore_errors=False)

    def test_backend_path_without_zip_extension(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            self.assertEquals(settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip', backend.get_path())

    def test_backend_path_with_zip_extension(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            self.assertNotEquals(settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip.zip', backend.get_path())
            self.assertEquals(settings.DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY+'testpath.zip', backend.get_path())

    def test_backend_open_archive_is_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.read_archive()

    def test_backend_open_readmode_false(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            backend = backend_mock.MockDevilryZipBackend(archive_path='testpath', readmode=False)
            with self.assertRaisesMessage(ValueError, 'Must be in readmode'):
                backend.read_archive()

    def test_backend_open_readmode_true(self):
        # Raises ValueError since the archive is None. This is just to test that the readmode
        # error doesnt kick in.
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath, readmode=False)
            backend.readmode = True
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.read_archive()

    def test_backend_add_file_readmode_true(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            backend = backend_mock.MockDevilryZipBackend(archive_path='testpath')
            with self.assertRaisesMessage(ValueError, 'readmode must be False to add files.'):
                backend.add_file('', None)

    def test_backend_close_archive_is_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.close_archive()

    def test_backend_size_archive_none(self):
        with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
            testpath = 'testpath'
            backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
            with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}{}.zip'.format(
                    self.backend_path, testpath)):
                backend.archive_size()

    def test_backend_is_compressed(self):
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
                f = open(filename, 'w')
                f.write(lorem_ipsum)
                f.close()

                # Write to backend
                backend.add_file('{}'.format(filename), open(filename, 'r'))
                backend.close_archive()

                # Read from created archive
                backend.readmode = True
                self.assertTrue(backend.archive_size() < os.stat(f.name).st_size)
                os.remove(f.name)

    def test_backend_open_after_close(self):
            # Test storage of zip archive locally
            # This test is mostly for testing the API and that files are stored correctly.
            with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                backend = backend_class(archive_path='testfile', readmode=False)

                # Create testfile
                filename = 'testfile.txt'
                f = open(filename, 'w')
                f.write('testcontent')
                f.close()

                # Write to backend
                backend.add_file('{}'.format(filename), open(filename, 'r'))
                backend.close_archive()
                backend.add_file('{}'.format('testfile2.txt'), open(filename, 'r'))
                backend.close_archive()
                os.remove(f.name)

                # Read from created archive
                backend.readmode = True
                archive = backend.get_archive()
                self.assertEquals('testcontent', archive.read(archive.namelist()[0]))
                self.assertEquals('testcontent', archive.read(archive.namelist()[1]))

    def test_backend_add_file(self):
            # Test storage of zip archive locally
            # This test is mostly for testing the API and that files are stored correctly.
            with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                backend = backend_class(archive_path='testfile1', readmode=False)

                # Create testfile
                filename = 'testfile.txt'
                f = open(filename, 'w')
                f.write('testcontent')
                f.close()

                # Write to backend
                backend.add_file('{}'.format(filename), open(filename, 'r'))
                backend.close_archive()
                os.remove(f.name)

                # Read from created archive
                backend.readmode = True
                archive = backend.get_archive()
                self.assertEquals('testcontent', archive.read(archive.namelist()[0]))

    def test_backend_add_file_deep_path(self):
            # Test storage of zip archive locally
            # This test is mostly for testing the API and that files are stored correctly.
            with self.settings(DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY=self.backend_path):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                storage_path = '{}/{}/{}'.format(1, 2, 'testarchive')
                backend = backend_class(archive_path=storage_path, readmode=False)

                # Create testfile
                filename = 'testfile.txt'
                f = open(filename, 'w')
                f.write('testcontent')
                f.close()

                # Write to backend
                backend.add_file('{}'.format(filename), open(filename, 'r'))
                backend.close_archive()
                os.remove(f.name)

                # Read from created archive
                backend.readmode = True
                archive = backend.get_archive()
                self.assertEquals('testcontent', archive.read(archive.namelist()[0]))
