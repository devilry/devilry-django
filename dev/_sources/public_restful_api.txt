
.. toctree::
    :hidden:

    restfulapi/administrator/index.rst
    restfulapi/examiner/index.rst
    restfulapi/student/index.rst

.. _public_restful_api:

==========================================
Public RESTful API
==========================================

********
APIs
********

* :ref:`restful_apiadministrator` --- Perform actions that require *administrator* permissions.
* :ref:`restful_apiexaminer` --- Perform actions that require *examiner* permissions.
* :ref:`restful_apistudent` --- Perform actions that require *student* permissions.




******************
HTTP status codes
******************


HTTP Success status codes
-------------------------

200 OK
    The request was successful. The requested data is returned.
201 CREATED
    Creation of a resource was successful. The created item is
    contained in the response.


.. _restful_api_error_statuscodes:

HTTP Error status codes
------------------------

400 Bad Request
    A parameter is invalid. The response body contains information about
    the error in a JSON encoded object with the following keys:

        errormessages
            Error messages not associated with any specific field.
        fielderrors
            Errors associated with a field name.
            An object where each *key* is a fieldname and each *value* is a
            string containing a field-specific error message.

401 Unauthorized
    Authorization required.
403 Forbidden
    Not authorized to access this page.
404 Not found
    Resource not found at the given url.

