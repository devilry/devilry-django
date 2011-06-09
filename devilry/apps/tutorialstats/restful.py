from ..restful.restview import ModelRestView
from ..restful.restful_api import restful_api
from simplified import StatConfig


@restful_api
class RestStatConfig(ModelRestView):
    class Meta:
        simplified = StatConfig
