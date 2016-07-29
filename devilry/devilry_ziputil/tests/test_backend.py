# Python imports
import os

# Django imports
from django.test import TestCase

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

    def test_backend_open_archive_is_none(self):
        testpath = 'testpath'
        backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
        with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}'.format(testpath)):
            backend.open_archive()

    def test_backend_open_readmode_false(self):
        backend = backend_mock.MockDevilryZipBackend(archive_path='', readmode=False)
        with self.assertRaisesMessage(ValueError, 'Must be in readmode'):
            backend.open_archive()

    def test_backend_close_archive_is_none(self):
        testpath = 'testpath'
        backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
        with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}'.format(testpath)):
            backend.close_archive()

    def test_backend_size_archive_none(self):
        testpath = 'testpath'
        backend = backend_mock.MockDevilryZipBackend(archive_path=testpath)
        with self.assertRaisesMessage(ValueError, 'Archive does not exist at {}'.format(testpath)):
            backend.archive_size()

    def test_backend_is_compressed(self):
        # Simply checks that the compressed archives size is less than the file written to it.
        with self.settings(DEVILRY_GROUP_ZIPFILE_DIRECTORY='devilry_testfiles/zipfiles'):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                storage_path = backend_class.get_storage_location() + '/testfile.zip'
                backend = backend_class(archive_path=storage_path, readmode=False)

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
                os.remove(backend.archive_path)

    def test_backend_add_file(self):
            # Test storage of zip archive locally
            # This test is mostly for testing the API and that files are stored correctly.
            with self.settings(DEVILRY_GROUP_ZIPFILE_DIRECTORY='devilry_testfiles/zipfiles'):
                mockregistry = backend_registry.MockableRegistry.make_mockregistry(
                    backend_mock.MockDevilryZipBackend
                )
                # Get backend and set storage path
                backend_class = mockregistry.get('default')
                storage_path = backend_class.get_storage_location() + '/testfile1.zip'
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
                archive = backend.open_archive()
                self.assertEquals('testcontent', archive.read(archive.namelist()[0]))
                os.remove(backend.archive_path)
