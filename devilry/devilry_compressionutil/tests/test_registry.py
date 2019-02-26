# Django imports
from django.test import TestCase

# Devilry imports
from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock


class TestBackendRegistry(TestCase):

    def test_get_backend(self):
        # Get backend from registry.
        mockregistry = backend_registry.MockableRegistry.make_mockregistry(
            backend_mock.MockDevilryZipBackend,
            backend_mock.MockDevilryZipBackendS3,
            backend_mock.MockDevilryZipBackendHeroku
        )

        self.assertEqual(backend_mock.MockDevilryZipBackend, mockregistry.get('default'))
        self.assertEqual(backend_mock.MockDevilryZipBackendS3, mockregistry.get('s3'))
        self.assertEqual(backend_mock.MockDevilryZipBackendHeroku, mockregistry.get('heroku'))

    def test_backend_registry_duplicate_error(self):
        # Raises error when adding the same backend more than once.
        with self.assertRaises(backend_registry.DuplicateBackendTypeError):
            backend_registry.MockableRegistry.make_mockregistry(
                backend_mock.MockDevilryZipBackend,
                backend_mock.MockDevilryZipBackend
            )
