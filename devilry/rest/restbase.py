class RestBase(object):
    """
    RESTful interface.
    """

    def create(self, **data):
        """
        Create object from the input ``data``.

        Should return a representation of the created object.
        """
        raise NotImplementedError()

    def read(self, id, **data):
        """
        Read and return the object identified by ``id``.

        May use ``data`` to limit/customize the response, however it _must_ work without ``data``.
        """
        raise NotImplementedError()

    def update(self, id, **data):
        """
        Update object identified by ``id`` from the input ``data``.

        Should return a representation of the updated object.
        """
        raise NotImplementedError()

    def delete(self, id, **data):
        """
        Delete the object identified by ``id``.

        May use ``data`` to customize the behavior, however it _must_ work without ``data``.
        """
        raise NotImplementedError()

    def list(self, **data):
        """
        List objects. Use data to provide the ability to limit the results.
        """
        raise NotImplementedError()

    def batch(self, create=[], update=[], delete=[]):
        """
        Create, update and/or delete many items in a single operation.

        The advantage of this approach over many create, update and delete requests are
        efficiency and the ability to do all operations in one transaction.
        """
        raise NotImplementedError()