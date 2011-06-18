from ..restful.restview import ModelRestView
from ..restful.restful_api import restful_api, UrlMapping
from ..restful.administrator import RestPeriod
from simplified import StatConfig


@restful_api
class RestStatConfig(ModelRestView):
    class Meta:
        simplified = StatConfig
        urlmap = {'period_url': UrlMapping(RestPeriod, 'period__id')}
