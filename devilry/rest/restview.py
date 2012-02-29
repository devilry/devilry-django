"""

"""
from django.http import HttpResponse, HttpResponseBadRequest

from jsondataconverter import JsonDataConverter
from xmldataconverter import XmlDataConverter
from yamldataconverter import YamlDataConverter
from htmldataconverter import HtmlDataConverter
from devilry.rest import input_content_type_detectors
from devilry.rest import output_content_type_detectors
import inputdata_handlers
import responsehandlers
import restmethod_routers
import output_data_postprocessors
import errorhandlers
from .error import InvalidInputContentTypeError
from .error import NotAcceptable


class RestView(object):
    """
    The ``RestView`` class is a Django view class that handles input/output to
    :class:`devilry.rest.restbase.RestBase`.

    See :meth:`.view` for details about how it handles each request.

    .. attribute:: restapicls

        A class implementing :class:`devilry.rest.restbase.RestBase`.

    .. attribute:: suffix_to_content_type_map

        Maps suffix to content type. Used to determine content-type from url-suffix.
        Defaults to::

            {"xml": "application/xml",
             "yaml": "application/yaml",
             "json": "application/json",
             "extjs.json": "application/extjsjson",
             "html": "text/html"}

    .. attribute:: input_data_preprocessors

        List of input data pre-processor callbacks. The callbacks have the following signature::

            match, input_data = f(request, input_data)

        The ``input_data`` of the first matching callback will be used. If no
        processor matches, the unchanged data will be used.
        Together with ``output_data_postprocessors`` this allows for wrapping
        certain content-types with extra data. By default, no input data
        pre-processors are registered.

    .. attribute:: output_data_postprocessors

        List of output data post-processor callbacks. See ``input_data_preprocessors``
        for more details. Callback signature::

            match, output_data = f(request, output_data, has_errors)

        The ``output_data`` of the first matching callback will be used. If no
        processor matches, the unchanged data will be used.

        Where ``has_errors`` is a boolean telling if the restful method
        completed with/without error.

        Defaults to:

            - :func:`.output_data_postprocessors.extjs`

    .. attribute:: output_content_type_detectors

        Output content type detectors detect the content type of the request data.
        Must be a list of callables with the following signature::

            content_type  = f(request, suffix)

        The first content_type that is not ``bool(content_type)==False`` will
        be used.

        Defaults to:

            - :func:`.output_content_type_detectors.devilry_accept_querystringparam`
            - :func:`.output_content_type_detectors.suffix`
            - :func:`.output_content_type_detectors.from_acceptheader`

    .. attribute:: input_content_type_detectors

        Similar to :attr:`output_content_type_detectors`, except for input/request
        instead of for output/response. Furthermore, the the callbacks take the
        output content-type as the third argument::

            content_type  = f(request, suffix, output_content_type)

        This is because few clients send the CONTENT_TYPE header, and falling back on
        output content-type is a mostly sane default.

    .. attribute:: inputdata_handlers

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
            - :func:`.inputdata_handlers.noinput_inputdata_handler`

    .. attribute:: dataconverters

        A dict of implementations of :class:`.dataconverter.DataConverter`.
        The key is a content-type. Data converters convert between python and some other format,
        such as JSON or XML.

        Typically used by :attr:`inputdata_handlers` and
        :attr:`response_handlers` to convert data input the content_type
        detected by one of the :attr:`output_content_type_detectors`.

        Defaults to:

            - ``"application/xml"``: :class:`.xmldataconverter.XmlDataConverter`
            - ``"application/yaml"``: :class:`.yamldataconverter.YamlDataConverter`
            - ``"application/json"``: :class:`.jsondataconverter.JsonDataConverter`
            - ``"application/extjsjson"``: :class:`.jsondataconverter.JsonDataConverter`
            - ``"text/html"``: :class:`.htmldataconverter.HtmlDataConverter`

    .. attribute:: restmethod_routers

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

    .. attribute:: response_handlers

        Response handlers are responsible for creating the response after the 
        rest method has been successfully invoked, and the output has been encoded.
        Signature::

            reponse = f(request, restapimethodname, output_content_type, encoded_output)

        The first response handler returning ``bool(response) == True`` is used. Defaults
        to:

            - :func:`.responsehandlers.extjs`
            - :func:`.responsehandlers.stricthttp`

    .. attribute:: errorhandlers

        Error handlers are functions that take an exception object as
        parameter, and returns a HTTP status code and error reponse data.
        Must be a list of callables with the following signature::

            statuscode, errordata = f(error)

        Defaults to:

            - :func:`.errorhandlers.clienterror`
            - :func:`.errorhandlers.django_validationerror`
    """
    suffix_to_content_type_map = {
        "xml": "application/xml",
        "yaml": "application/yaml",
        "json": "application/json",
        "extjs.json": "application/extjsjson",
        "html": "text/html"
    }

    input_data_preprocessors = []
    output_data_postprocessors = [
        output_data_postprocessors.extjs
    ]

    output_content_type_detectors = [
        # This order is chosen because the "common" case is to use accept header, however when
        # the user does something special, like adding a querystring param or suffix, they do
        # it intentionally.
        output_content_type_detectors.devilry_accept_querystringparam,
        output_content_type_detectors.suffix,
        output_content_type_detectors.from_acceptheader
    ]

    input_content_type_detectors = [
        input_content_type_detectors.from_content_type_header,
        input_content_type_detectors.use_output_content_type
    ]

    inputdata_handlers = [
        inputdata_handlers.getqrystring_inputdata_handler,
        inputdata_handlers.rawbody_inputdata_handler,
        inputdata_handlers.noinput_inputdata_handler
    ]

    dataconverters = {
        "application/xml": XmlDataConverter,
        "application/yaml": YamlDataConverter,
        "application/json": JsonDataConverter,
        "application/extjsjson": JsonDataConverter,
        "text/html": HtmlDataConverter
    }
    restmethod_routers = [
        restmethod_routers.post_to_create,
        restmethod_routers.get_with_id_to_read,
        restmethod_routers.put_with_id_to_update,
        restmethod_routers.delete_to_delete,
        restmethod_routers.get_without_id_to_list,
        restmethod_routers.put_without_id_to_batch
    ]
    response_handlers = [
        responsehandlers.extjs,
        responsehandlers.stricthttp
    ]

    errorhandlers = [
        errorhandlers.clienterror,
        errorhandlers.django_validationerror
    ]


    def __init__(self, restapicls, apiname, apiversion):
        self.restapicls = restapicls
        self.apiname = apiname
        self.apiversion = apiversion

    def view(self, request, id_and_suffix=None):
        """
        Called each time the view is requested.

        It delegates most of its logic to *functionchains* that handles various
        clearly separated tasks. A *functionchain* is a list of functions where
        the result of the first successfully executed function is used.

        A high level overview of what the method does:

        1. Detect output and input content types using the
           :attr:`output_content_type_detectors` and
           :attr:`input_content_type_detectors` *functionchain*.
           Respond with ``HttpResponseBadRequest`` if this fails.
        2. Parse the input data using the :attr:`inputdata_handlers` *functionchain*.
        3. Preprocess input data using the :attr:`input_data_preprocessors` *functionchain*.
        4. Detect the appropriate method in the ``restapicls`` using the
           :attr:`restmethod_routers` *functionchain*. Return HTTP 406 if no
           method is found.
        5. Call the detected ``restapicls`` method. If the function raises an
           exception:

               - Handle the error using the :attr:`errorhandlers` *functionchain*.
               - Respond with HTTP 406 if if the method raises
                 :exc:`NotImplementedError` (unless a custom error handler should catch this).
               - Re-raise the exception if no errorhandler handles it. This
                 will normally lead to a 500 servererror response.

        6. Postprocess the ouput data (output from the ``restapicls`` method or
           an errorhandler) using the :attr:`output_data_postprocessors`
           *functionchain*.
        7. Create a Django response using the :attr:`response_handlers` *functionchain*.
        """
        id, suffix = self.parse_id_and_suffix(id_and_suffix)
        self.request = request
        try:
            self.output_content_type = self.get_output_content_type(suffix)
            self.input_content_type, self.input_charset = self.get_input_content_type(suffix)
        except NotAcceptable, e:
            return HttpResponseBadRequest(str(e))
        input_data = self.parse_input()
        input_data = self.preprocess_input_data(input_data)

        method = request.method
        output = None
        for restmethod_route in self.restmethod_routers:
            match = restmethod_route(request, id, input_data)
            if match:
                restapimethodname, kwargs = match
                try:
                    return self.call_restapi(restapimethodname, kwargs)
                except NotImplementedError:
                    return HttpResponse("'{0}' is not supported.".format(restapimethodname), status=406)
        return HttpResponse("No restmethod route found.", status=406)


    def _process_data(self, processorlist, content_type, data, *extraargs):
        for processor in processorlist:
            match, processed_data = processor(self.request, data, *extraargs)
            if match:
                return processed_data
        return data

    def preprocess_input_data(self, input_data):
        return self._process_data(self.input_data_preprocessors, self.input_content_type, input_data)

    def postprocess_output_data(self, output_data, successful):
        return self._process_data(self.output_data_postprocessors, self.output_content_type, output_data, successful)

    def parse_id_and_suffix(self, id_and_suffix):
        id = None
        suffix = None
        if id_and_suffix:
            split = id_and_suffix.split('.', 1)
            id = split[0]
            if id == "":
                id = None
            if len(split) == 2:
                suffix = split[1]
        return id, suffix

    def call_restapi(self, restapimethodname, kwargs):
        restapi = self.restapicls(apiname=self.apiname, apiversion=self.apiversion, user=self.request.user)
        restmethod = getattr(restapi, restapimethodname)
        statuscodehint = None
        try:
            output = restmethod(**kwargs)
        except Exception, e:
            statuscodehint, output = self.error_handler(e)
            successful = False
        else:
            successful = True
        output = self.postprocess_output_data(output, successful=successful)
        encoded_output = self.encode_output(output)
        return self.create_response(encoded_output, restapimethodname, statuscodehint)

    def error_handler(self, error):
        for errorhandler in self.errorhandlers:
            statuscode, errordata = errorhandler(error)
            if statuscode and errordata:
                return statuscode, errordata
        raise # Re-raise the exception if it is not handled by any errorhandler

    def _get_content_type(self, detectors, suffix, *extraargs):
        for content_type_detector in detectors:
            content_type = content_type_detector(self.request, suffix,
                                                 self.suffix_to_content_type_map,
                                                 self.dataconverters.keys(), *extraargs)
            if content_type:
                return content_type
        return None

    def get_output_content_type(self, suffix):
        content_type = self._get_content_type(self.output_content_type_detectors, suffix)
        if not content_type:
            raise NotAcceptable('No acceptable output content type detected.')
        return content_type

    def get_input_content_type(self, suffix):
        content_type = self._get_content_type(self.input_content_type_detectors, suffix, self.output_content_type)
        if not content_type:
            raise InvalidInputContentTypeError('No acceptable input content type detected.')
        return content_type

    def parse_input(self):
        for input_data_handler in self.inputdata_handlers:
            match, data = input_data_handler(self.request, self.input_content_type, self.dataconverters)
            if match:
                if not isinstance(data, dict):
                    raise ValueError("Input data handlers must return (bool, dict).")
                return data
        return {}

    def create_response(self, encoded_output, restapimethodname, statuscodehint):
        for response_handler in self.response_handlers:
            response = response_handler(self.request, restapimethodname,
                                        self.output_content_type,
                                        encoded_output, statuscodehint)
            if response:
                return response
        raise ValueError(
            "No matching response_handler. You should provide one that always matches at the end of the chain.")

    def encode_output(self, output):
        dataconverter = self.dataconverters[self.output_content_type]
        return dataconverter.fromPython(output, self.dataconverters.keys())


    @classmethod
    def as_view(cls, *initargs, **initkwargs):
        def view(request, id_and_suffix):
            self = cls(*initargs, **initkwargs)
            return self.view(request, id_and_suffix)

        return view
