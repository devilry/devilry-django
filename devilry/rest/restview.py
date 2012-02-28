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


class RestView():
    """
    Django view that handles input/output to :class:`devilry.rest.restbase.RestBase`.
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
