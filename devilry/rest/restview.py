"""

"""
from django.http import HttpResponse, HttpResponseBadRequest

from .error import InvalidInputContentTypeError
from .error import NotAcceptable
import default


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
                 response_handlers=default.RESPONSEHANDLERS,
                 errorhandlers=default.ERRORHANDLERS):
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
        self.errorhandlers = errorhandlers

    def view(self, request, id_and_suffix=None):
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
