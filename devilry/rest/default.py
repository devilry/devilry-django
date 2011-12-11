from devilry.dataconverter.jsondataconverter import JsonDataConverter
from devilry.dataconverter.xmldataconverter import XmlDataConverter
from devilry.dataconverter.yamldataconverter import YamlDataConverter
from devilry.dataconverter.htmldataconverter import HtmlDataConverter
from devilry.rest import input_content_type_detectors
from devilry.rest import output_content_type_detectors
import inputdata_handlers
import responsehandlers
import restmethod_routers
import output_data_postprocessors


SUFFIX_TO_CONTENT_TYPE_MAP = {
    "xml": "application/xml",
    "yaml": "application/yaml",
    "json": "application/json",
    "extjs.json": "application/json+extjs",
    "html": "text/html"
}

INPUT_DATA_PREPROCESSORS = {
}
OUTPUT_DATA_POSTPROCESSORS = {
    "application/json+extjs": output_data_postprocessors.extjs
}

OUTPUT_CONTENT_TYPE_DETECTORS = [
    # This order is chosen because the "common" case is to use accept header, however when
    # the user does something special, like adding a querystring param or suffix, they do
    # it intentionally.
    output_content_type_detectors.devilry_accept_querystringparam,
    output_content_type_detectors.suffix,
    output_content_type_detectors.from_acceptheader
]

INPUT_CONTENT_TYPE_DETECTORS = [
    input_content_type_detectors.from_content_type_header,
    input_content_type_detectors.use_output_content_type
]

INPUTDATA_HANDLERS = [
    inputdata_handlers.getqrystring_inputdata_handler,
    inputdata_handlers.rawbody_inputdata_handler
]

DATACONVERTERS = {
    "application/xml": XmlDataConverter,
    "application/yaml": YamlDataConverter,
    "application/json": JsonDataConverter,
    "application/json+extjs": JsonDataConverter,
    "text/html": HtmlDataConverter
}
RESTMETHOD_ROUTES = [
    restmethod_routers.post_to_create,
    restmethod_routers.get_with_id_to_read,
    restmethod_routers.put_with_id_to_update,
    restmethod_routers.delete_to_delete,
    restmethod_routers.get_without_id_to_list,
    restmethod_routers.put_without_id_to_batch
]
RESPONSEHANDLERS = [
    responsehandlers.stricthttp
]
