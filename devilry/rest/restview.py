from django.http import HttpResponseNotAllowed

from devilry.rest.error import NotFoundError
from devilry.dataconverter.jsondataconverter import JsonDataConverter
import inputdata_handlers
import responsehandlers


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
DEFAULT_RESPONSEHANDLERS = [
    responsehandlers.stricthttp
]

class RestView():
    def __init__(self, restapicls,
                 suffix_to_content_type_map=DEFAULT_SUFFIX_TO_CONTENT_TYPE_MAP,
                 default_content_type="application/json",
                 inputdata_handlers=DEFAULT_INPUTDATA_HANDLERS,
                 dataconverters=DEFAULT_DATACONVERTERS,
                 response_handlers=DEFAULT_RESPONSEHANDLERS):
        self.restapi = restapicls()
        self.suffix_to_content_type_map = suffix_to_content_type_map
        self.default_content_type = default_content_type
        self.inputdata_handlers = inputdata_handlers
        self.dataconverters = dataconverters
        self.response_handlers = response_handlers

    def get(self, id):
        if id == None:
            self.crud_method = 'list'
            try:
                return self.restapi.crud_list(**self.input_data)
            except NotImplementedError:
                raise NotFoundError('GET method with no identifier (list) is not supported.')
        else:
            self.crud_method = 'read'
            try:
                return self.restapi.crud_read(id, **self.input_data)
            except NotImplementedError:
                raise NotFoundError('GET method with identifier (read) is not supported.')

    def post(self):
        self.crud_method = 'create'
        return self.restapi.crud_create(**self.input_data)

    def put(self, id):
        self.crud_method = 'update'
        return self.restapi.crud_update(id, **self.input_data)

    def delete(self, id):
        self.crud_method = 'delete'
        return self.restapi.crud_delete(id, **self.input_data)

    def view(self, request, id=None, suffix=None):
        self.suffix = suffix
        self.request = request
        self.detect_content_types()
        self.input_data = self.parse_input()

        method = request.method
        output = None
        if method in self.restapi.supported_methods:
            try:
                output = getattr(self, method.lower())(id)
            except Exception, e:
                return self.error_handler(e)
        else:
            return HttpResponseNotAllowed(self.restapi.suppored_methods)
        encoded_output = self.encode_output(output)
        return self.create_response(encoded_output)

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

    def create_response(self, encoded_output):
        for response_handler in self.response_handlers:
            match, response = response_handler(self.request, self.crud_method,
                                               self.output_content_type, encoded_output)
            if match:
                return response
        raise ValueError("No matching response_handler. You should provide one that always matches at the end of the chain.")

    def encode_output(self, output):
        dataconverter = self.dataconverters.get(self.output_content_type, self.dataconverters[self.default_content_type])
        return dataconverter.fromPython(output)


    @classmethod
    def as_view(cls, *initargs, **initkwargs):
        def view(request, id=None, suffix=None):
            self = cls(*initargs, **initkwargs)
            return self.view(request, id)

        return view