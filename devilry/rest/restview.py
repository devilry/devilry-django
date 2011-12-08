from django.http import HttpResponseNotAllowed, HttpResponseBadRequest

from devilry.rest.error import NotFoundError
from devilry.dataconverter.jsondataconverter import JsonDataConverter
import inputdata_handlers
import responsehandlers
import restmethod_roters


DEFAULT_SUFFIX_TO_CONTENT_TYPE_MAP = {
    "xml": "application/xml",
    "json": "application/json"
}

DEFAULT_INPUTDATA_HANDLERS = [
    inputdata_handlers.getqrystring_inputdata_handler,
    inputdata_handlers.rawbody_inputdata_handler
]
DEFAULT_DATACONVERTERS = {
    "application/xml": None,
    "application/json": JsonDataConverter
}
DEFAULT_RESTMETHOD_ROUTES = [
    restmethod_roters.post_to_create,
    restmethod_roters.get_with_id_to_read,
    restmethod_roters.put_with_id_to_update,
    restmethod_roters.delete_to_delete,
    restmethod_roters.get_without_id_to_list,
    restmethod_roters.put_without_id_to_batch
]
DEFAULT_RESPONSEHANDLERS = [
    responsehandlers.stricthttp
]

class RestView():
    def __init__(self, restapicls,
                 suffix_to_content_type_map=DEFAULT_SUFFIX_TO_CONTENT_TYPE_MAP,
                 default_content_type="application/json",
                 inputdata_handlers=DEFAULT_INPUTDATA_HANDLERS,
                 dataconverters=DEFAULT_DATACONVERTERS,
                 restmethod_routers=DEFAULT_RESTMETHOD_ROUTES,
                 response_handlers=DEFAULT_RESPONSEHANDLERS):
        """
        :param restapicls:
            A class implementing :class:`devilry.rest.restbase.RestBase`.
        :param suffix_to_content_type_map:
            Maps suffix to content type. Used to determine content-type from url-suffix.
        :param default_content_type:
            Default in/out content-type.
        :param inputdata_handlers:
            Input data handlers convert input data into a dict.
            Must be a list of callables with the following signature::

                match, data = f(request, input_content_type, dataconverters)

            The first input data handler returning ``match==True`` is be used.
                
            See :mod:`devilry.rest.inputdata_handlers` for implementations.
            
            Input data can come in many different formats and from different sources.
            Examples are such XML in request body, query string and JSON embedded in
            a query string parameter.
        :param dataconverters:
            A list of implementations of :class:`devilry.dataconverter.dataconverter.DataConverter`.
            Data converters convert between python and some other format, such as JSON or XML.
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
        self.restapi = restapicls()
        self.suffix_to_content_type_map = suffix_to_content_type_map
        self.default_content_type = default_content_type
        self.inputdata_handlers = inputdata_handlers
        self.dataconverters = dataconverters
        self.restmethod_routers = restmethod_routers
        self.response_handlers = response_handlers

    def view(self, request, id=None, suffix=None):
        self.suffix = suffix
        self.request = request
        self.detect_content_types()
        input_data = self.parse_input()

        method = request.method
        output = None
        if request.method in self.restapi.supported_methods:
            for restmethod_route in self.restmethod_routers:
                match = restmethod_route(request, id, input_data)
                if match:
                    restapimethodname, args, kwargs = match
                    return self.call_restapi(restapimethodname, args, kwargs)
            return HttpResponseBadRequest("No restmethod route found.")
        else:
            return HttpResponseNotAllowed(self.restapi.suppored_methods)

    def call_restapi(self, restapimethodname, args, kwargs):
        try:
            output = getattr(self.restapi, restapimethodname)(*args, **kwargs)
        except Exception, e:
            return self.error_handler(e)
        else:
            encoded_output = self.encode_output(output)
            return self.create_response(encoded_output, restapimethodname)

    def detect_content_types(self):
        """
        Detect input/output content types.
        """
        self.output_content_type = self.get_output_content_type()
        self.input_content_type = self.get_input_content_type()

    def get_output_content_type(self):
        return self.suffix_to_content_type_map.get(self.suffix, self.default_content_type)

    def get_input_content_type(self):
        return self.request.META.get('CONTENT_TYPE', self.output_content_type)

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
        dataconverter = self.dataconverters.get(self.output_content_type,
                                                self.dataconverters[self.default_content_type])
        return dataconverter.fromPython(output)


    @classmethod
    def as_view(cls, *initargs, **initkwargs):
        def view(request, id=None, suffix=None):
            self = cls(*initargs, **initkwargs)
            return self.view(request, id)

        return view