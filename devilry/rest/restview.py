"""

"""
import inspect
from django.http import HttpResponse, HttpResponseBadRequest

from devilry.rest.error import InvalidContentTypeError
from devilry.rest.httpacceptheaderparser import HttpAcceptHeaderParser
import default
from devilry.rest.utils import subdict


class RestView():
    """
    Django view that handles input/output to :class:`devilry.rest.restbase.RestBase`.
    """
    def __init__(self, restapicls,
                 apiname, apiversion,
                 suffix_to_content_type_map=default.SUFFIX_TO_CONTENT_TYPE_MAP,
                 input_data_preprocessors=default.INPUT_DATA_PREPROCESSORS,
                 output_data_postprocessors=default.OUTPUT_DATA_POSTPROCESSORS,
                 output_content_type_detectors=default.OUTPUT_CONTENT_TYPE_DETECTORS,
                 input_content_type_detectors=default.INPUT_CONTENT_TYPE_DETECTORS,
                 inputdata_handlers=default.INPUTDATA_HANDLERS,
                 dataconverters=default.DATACONVERTERS,
                 restmethod_routers=default.RESTMETHOD_ROUTES,
                 response_handlers=default.RESPONSEHANDLERS):
        """
        :param restapicls:
            A class implementing :class:`devilry.rest.restbase.RestBase`.
        :param suffix_to_content_type_map:
            Maps suffix to content type. Used to determine content-type from url-suffix.

        :param input_data_preprocessors:
            Dict of input data post-processor callbacks by content-type. If the input content-type
            matches a key in the dict, the corresponding callback is called with the input data
            as argument. Together with ``output_data_postprocessors`` this allows for wrapping
            certain content-types with extra data. Example of use is to add data that is requried
            by a javascript library, such as the successful attribute required by ExtJS.
        :param output_data_postprocessors:
            Dict of output data post-processor callbacks by content-type. See ``input_data_preprocessors``
            for more details.

        :param output_content_type_detectors:
            Input content type detectors detect the content type of the request data.
            Must be a list of callables with the following signature::

                content_type  = f(request, suffix)

            The first content_type that is not ``bool(content_type)==False`` will
             be used.
        :param input_content_type_detectors:
            Similar to ``output_content_type_detectors``, except for input/request
            instead of for output/response. Furthermore, the the callbacks take the
            output content-type as the third argument::

                content_type  = f(request, suffix, output_content_type)

            This is because few clients send the CONTENT_TYPE header, and falling back on
            output content-type is a mostly sane default.

        :param inputdata_handlers:
            Input data handlers convert input data into a dict. Input data can come from several sources:

                - Querystring
                - Paramater in querystring
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
        :param dataconverters:
            A dict of implementations of :class:`devilry.dataconverter.dataconverter.DataConverter`.
            The key is a content-type. Data converters convert between python and some other format,
            such as JSON or XML.

            Typically used by ``input_datahandlers`` and ``response_handlers`` to convert data
             input the content_type detected by one of the ``output_content_type_detectors``.
        :param restmethod_routers:
            A list of callables with the following signature::

                restapimethodname, args, kwargs = f(request, id, input_data)

            ``None`` must be returned if the route does not match.

            Restmetod routes takes determines which method in the :class:`devilry.rest.restbase.RestBase`
            interface to call, and the arguments to use for the call.
        :param response_handlers:
            Response handlers are responsible for creating responses.
            Signature::

                reponse = f(request, restapimethodname, output_content_type, encoded_output)

            The first response handler returning ``bool(response) == True`` is used.
        """
        self.restapicls = restapicls
        self.apiname = apiname
        self.apiversion = apiversion
        self.input_data_preprocessors = input_data_preprocessors
        self.output_data_postprocessors = output_data_postprocessors
        self.output_content_type_detectors = output_content_type_detectors
        self.input_content_type_detectors = input_content_type_detectors
        self.suffix_to_content_type_map = suffix_to_content_type_map
        self.inputdata_handlers = inputdata_handlers
        self.dataconverters = dataconverters
        self.restmethod_routers = restmethod_routers
        self.response_handlers = response_handlers

    def view(self, request, id_and_suffix=None):
        id, suffix = self.parse_id_and_suffix(id_and_suffix)
        self.request = request
        try:
            self.output_content_type = self.get_output_content_type(suffix)
            self.input_content_type = self.get_input_content_type(suffix)
        except InvalidContentTypeError, e:
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


    def _process_data(self, processormap, content_type, data):
        processor = processormap.get(content_type)
        if processor:
            data = processor(data)
        return data

    def preprocess_input_data(self, input_data):
        return self._process_data(self.input_data_preprocessors, self.input_content_type, input_data)

    def postprocess_output_data(self, output_data):
        return self._process_data(self.output_data_postprocessors, self.output_content_type, output_data)

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
        try:
            output = restmethod(**kwargs)
        except Exception, e:
            return self.error_handler(e)
        else:
            output = self.postprocess_output_data(output)
            encoded_output = self.encode_output(output)
            return self.create_response(encoded_output, restapimethodname)


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
            raise InvalidContentTypeError('Not output content type detected.')
        return content_type

    def get_input_content_type(self, suffix):
        content_type = self._get_content_type(self.input_content_type_detectors, suffix, self.output_content_type)
        if not content_type:
            raise InvalidContentTypeError('Not input content type detected.')
        return content_type

    def parse_input(self):
        for input_data_handler in self.inputdata_handlers:
            match, data = input_data_handler(self.request, self.input_content_type, self.dataconverters)
            if match:
                if not isinstance(data, dict):
                    raise ValueError("Input data handlers must return (bool, dict).")
                return data
        return {}

    def error_handler(self, error):
        raise # Will result in server error unless catched by some middleware

    def create_response(self, encoded_output, restapimethodname):
        for response_handler in self.response_handlers:
            response = response_handler(self.request, restapimethodname,
                                        self.output_content_type, encoded_output)
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