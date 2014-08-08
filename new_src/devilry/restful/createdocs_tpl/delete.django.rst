Delete a {{doc.model_verbose_name}}.

The underlying data model where the item is deleted from is defined in :class:`{{doc.modelclspath}}`.
The :ref:`simplified` that the server forwards this request to is
:meth:`{{doc.simplifiedclspath}}.delete`.


********
Request
********

Example
################

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}



Required request parameters
###########################

id
--------------

The unique identifier of a {{doc.model_verbose_name}}. You will typically get
this id in response from a search.


**************
Response
**************


On success
##########

As long as the {{doc.model_verbose_name}} is deleted without an error, the
response is *HTTP 200* with a JSON object containing the id in the response body.


Example
-------

.. code-block:: javascript

    200 OK

    {
        id: 10
    }


On error
########

On errors, we respond with one of the :ref:`restful_api_error_statuscodes`
