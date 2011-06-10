from ..restful.restview import ModelRestView
from ..restful.restful_api import restful_api
from ..restful.extjs import extjs_modelapi, ExtJsMixin
from simplified import StatConfig


@extjs_modelapi
@restful_api
class RestStatConfig(ModelRestView, ExtJsMixin):
    class Meta:
        simplified = StatConfig
