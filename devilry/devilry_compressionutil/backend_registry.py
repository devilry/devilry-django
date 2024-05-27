from ievv_opensource.utils.singleton import Singleton


class DuplicateBackendTypeError(Exception):
    """
    Exception raised when trying to add multiple :class:`.~devilry.devilry_ziputil.backends.PythonZipFileBackend`
    with same ID.
    """


class Registry(Singleton):
    """
    Registry for subclasses of
    :class:`~devilry.devilry_ziputil.backends.backends_base.PythonZipFileBackend`.
    """
    def __init__(self):
        super(Registry, self).__init__()
        self._backendclasses = {}

    def __get_class_path(self):
        """
        Get class path.

        Returns:
            Classpath.
        """
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def add(self, backend):
        """
        Add a backend class.

        Args:
            backend: backend class.
        """
        if backend.backend_id in self._backendclasses:
            raise DuplicateBackendTypeError('Duplicate backend id in {}: {}'.format(
                self.__get_class_path(), backend.backend_id
            ))
        self._backendclasses[backend.backend_id] = backend

    def get(self, backend_id):
        """
        Get backend class.

        Args:
            backend_id: ID of backend class.

        Returns:
            :class:`~devilry.devilry_ziputil.backends.backends_base.PythonZipFileBackend` subclass or ``None``.
        """
        try:
            backend_class = self._backendclasses[backend_id]
        except KeyError:
            return None
        return backend_class


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`.Registry` for tests.
    """

    def __init__(self):
        self._instance = None
        super(MockableRegistry, self).__init__()

    @classmethod
    def make_mockregistry(cls, *backend_classes):
        """
        Create a mocked instance of Registry.

        Args:
            *backend_classes: Backends to add.

        Returns:
            MockableRegistry: An object of this class with the ``backend_classes`` registered.
        """
        mockregistry = cls()
        for backend_class in backend_classes:
            mockregistry.add(backend_class)
        return mockregistry
