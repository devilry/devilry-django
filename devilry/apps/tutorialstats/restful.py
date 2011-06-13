from ..restful.restview import ModelRestView
from ..restful.restful_api import restful_api, UrlMapping
from ..restful.extjs import extjs_modelapi, ExtJsMixin
from ..restful.administrator import RestPeriod
from simplified import StatConfig


@extjs_modelapi
@restful_api
class RestStatConfig(ModelRestView, ExtJsMixin):
    class Meta:
        simplified = StatConfig
        urlmap = {'period_url': UrlMapping(RestPeriod, 'period__id')}
