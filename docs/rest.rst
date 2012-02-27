.. _rest:

===============================================================
:mod:`devilry.rest` --- General purpose REST framework
===============================================================


.. currentmodule:: devilry.rest


About RESTful web services
##########################

http://en.wikipedia.org/wiki/Representational_State_Transfer#RESTful_web_services

Relation to restful
###################

Unlike :ref:`restful`, this is a general purpose REST interface library for
writing any RESTful interface, not just interfaces with a direct mapping to the
Django ORM.


.. _rest-for-users:

Using the REST APIs
#####################

If you are only using the rest APIs, and not creating them, this section is for you.


Content types
=============

The REST APIs generate data that can be serialized/deserialized on several formats:

- JSON --- application/json
- YAML --- application/yaml
- XML --- application/xml
- ExtJS flavoured JSON --- application/extjsjson


Output content type --- ACCEPT
------------------------------
The content type for output from the APIs is normally specified using a HTTP
accept header in the HTTP request::

    GET http://devilry.example.com/path/to/api/
    Accept: application/json

However you can also use the ``_devilry_accept`` querystring parameter::

    GET http://devilry.example.com/path/to/api/?_devilry_accept=application/json

Or suffix::

    GET http://devilry.example.com/path/to/api/1.json

Note that suffix also works on ``/``, even if it looks a bit strange::

    GET http://devilry.example.com/path/to/api/.json


Input content type
------------------

Normally you wont need to specify an input content type --- it will fall back
on the output content type. However, if you want to send data encoded in format,
and receive the response encoded in another, this is specified using
the ``Content-type`` HTTP header::

    GET http://devilry.example.com/path/to/api/
    Accept: application/xml
    Content-type: application/json


Parameters
==========

Parameters are given in one of the following ways:

- `Request body`_
- `Querystring`_


Request body
------------

Get the input parameters from the body of the HTTP request. This is usually
used for POST and PUT requests, however it should work for GET requests in
modern browsers. Example::


    POST http://devilry.example.com/path/to/api/
    Accept: application/json

    {stuff: 10, somethingelse: 'Hello world'}


Querystring
-----------

The querystring is the part after ? in the url. E.g.: if the ``/path/to/api/``
API required a numeric parameter named ``stuff``, we would specify it using::

    GET http://devilry.example.com/path/to/api/?stuff=10

Lets say the API also supported a ``search`` parameter, we could specify both
``stuff`` and ``search``::

    GET http://devilry.example.com/path/to/api/?stuff=10&search=something

.. note::

    Querystring can only be used for parameters to GET requests.



API
############################

Errors
========
.. automodule:: devilry.rest.error

RestBase
========
.. autoclass:: devilry.rest.restbase.RestBase

Input data handlers
===================
.. automodule:: devilry.rest.inputdata_handlers

Output content type detectors
=============================
.. automodule:: devilry.rest.output_content_type_detectors

Output data postprocessors
=============================
.. automodule:: devilry.rest.output_data_postprocessors

Restmethod routers
==================
.. automodule:: devilry.rest.restmethod_routers

Responsehandlers
================
.. automodule:: devilry.rest.responsehandlers


RestView
========
.. class:: devilry.rest.restview.RestView

    :param restapicls:
        A class implementing :class:`devilry.rest.restbase.RestBase`.
    :param suffix_to_content_type_map:
        Maps suffix to content type. Used to determine content-type from url-suffix.
        Defaults to::

            {"xml": "application/xml",
             "yaml": "application/yaml",
             "json": "application/json",
             "extjs.json": "application/extjsjson",
             "html": "text/html"}

    :param input_data_preprocessors:
        List of input data pre-processor callbacks. The callbacks have the following signature::

            match, input_data = f(request, input_data)

        The ``input_data`` of the first matching callback will be used. If no
        processor matches, the unchanged data will be used.
        Together with ``output_data_postprocessors`` this allows for wrapping
        certain content-types with extra data. By default, no input data
        pre-processors are registered.

    :param output_data_postprocessors:
        List of output data post-processor callbacks. See ``input_data_preprocessors``
        for more details. Callback signature::

            match, output_data = f(request, output_data, has_errors)

        The ``output_data`` of the first matching callback will be used. If no
        processor matches, the unchanged data will be used.

        Where ``has_errors`` is a boolean telling if the restful method
        completed with/without error.

        Defaults to:

            - :func:`.output_data_postprocessors.extjs`

    :param output_content_type_detectors:
        Output content type detectors detect the content type of the request data.
        Must be a list of callables with the following signature::

            content_type  = f(request, suffix)

        The first content_type that is not ``bool(content_type)==False`` will
        be used.

        Defaults to:

            - :func:`.output_content_type_detectors.devilry_accept_querystringparam`
            - :func:`.output_content_type_detectors.suffix`
            - :func:`.output_content_type_detectors.from_acceptheader`

    :param input_content_type_detectors:
        Similar to ``output_content_type_detectors``, except for input/request
        instead of for output/response. Furthermore, the the callbacks take the
        output content-type as the third argument::

            content_type  = f(request, suffix, output_content_type)

        This is because few clients send the CONTENT_TYPE header, and falling back on
        output content-type is a mostly sane default.

    :param inputdata_handlers:
        Input data handlers convert input data into a dict. Input data can come
        from several sources:

            - Querystring
            - Parameter in querystring
            - Request body

        Therefore, we need to check for data in several places. Instead of hardcoding this
        checking, we accept a list of callables that does the checking.

        Must be a list of callables with the following signature::

            match, data = f(request, input_content_type, dataconverters)

        The first input data handler returning ``match==True`` is be used.
            
        See :mod:`devilry.rest.inputdata_handlers` for implementations.
        
        Input data can come in many different formats and from different sources.
        Examples are such XML in request body, query string and JSON embedded in
        a query string parameter.

        Defaults to:

            - :func:`.inputdata_handlers.getqrystring_inputdata_handler`
            - :func:`.inputdata_handlers.rawbody_inputdata_handler`
            

    :param dataconverters:
        A dict of implementations of :class:`devilry.dataconverter.dataconverter.DataConverter`.
        The key is a content-type. Data converters convert between python and some other format,
        such as JSON or XML.

        Typically used by ``input_datahandlers`` and ``response_handlers`` to convert data
        input the content_type detected by one of the ``output_content_type_detectors``.

        Defaults to:

            - ``"application/xml"``: :class:`devilry.dataconverter.xmldataconverter.XmlDataConverter`
            - ``"application/yaml"``: :class:`devilry.dataconverter.yamldataconverter.YamlDataConverter`
            - ``"application/json"``: :class:`devilry.dataconverter.jsondataconverter.JsonDataConverter`
            - ``"application/extjsjson"``: :class:`devilry.dataconverter.jsondataconverter.JsonDataConverter`
            - ``"text/html"``: :class:`devilry.dataconverter.htmldataconverter.HtmlDataConverter`

    :param restmethod_routers:
        A list of callables with the following signature::

            restapimethodname, args, kwargs = f(request, id, input_data)

        ``None`` must be returned if the route does not match.

        Restmetod routes determines which method in the
        :class:`.restbase.RestBase` interface to call, and the arguments to
        use for the call. Defaults to:

            - :func:`.restmethod_routers.post_to_create`
            - :func:`.restmethod_routers.get_with_id_to_read`
            - :func:`.restmethod_routers.put_with_id_to_update`
            - :func:`.restmethod_routers.delete_to_delete`
            - :func:`.restmethod_routers.get_without_id_to_list`
            - :func:`.restmethod_routers.put_without_id_to_batch`

    :param response_handlers:
        Response handlers are responsible for creating the response after the 
        rest method has been successfully invoked, and the output has been encoded.
        Signature::

            reponse = f(request, restapimethodname, output_content_type, encoded_output)

        The first response handler returning ``bool(response) == True`` is used. Defaults
        to:

            - :func:`.responsehandlers.stricthttp`

    .. method:: error_handler(error)

        Override this method to handle errors. The ``error`` parameter is the
        catched exception. The function defaults to re-raising the exception,
        which will result is server-error unless some Django middleware caches
        the error. Example::

            class MyRestView(RestView):
                def error_handler(self, error):
                    try:
                        raise # Re-raise the error
                    except MyCustomError, e:
                        return dict(error=str(e))


@indata
========
.. automodule:: devilry.rest.indata

Test utilities
==============
.. automodule:: devilry.rest.testutils
