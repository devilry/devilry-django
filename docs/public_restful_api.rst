
.. toctree::
    :hidden:

    restfulapi/administrator/index.rst

.. _public_restful_api:

==========================================
Public RESTful API
==========================================


HTTP status codes
-----------------

200 OK
    The request was successful. The requested data is returned.
201 CREATED
    Creation of a resource was successful. The created item is
    contained in the response.
400 Bad Request
    A parameter is invalid. The response contains the error message.
401 Unauthorized
    Authorization required.
403 Forbidden
    Not authorized to access this page.
404 Not found
    Resource not found at the given url.



APIs
----

* :ref:`restful_apiadministrator`
* :ref:`restful_apiexaminer`
* :ref:`restful_apistudent`
