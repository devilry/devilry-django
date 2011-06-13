from ..simplified.administrator import Node, Subject, Period
from restview import ModelRestView
from restful_api import restful_api
import extjs


@extjs.extjs_modelapi
@restful_api
class RestNode(ModelRestView, extjs.ExtJsMixin):
    class Meta:
        simplified = Node


@extjs.extjs_modelapi
@restful_api
class RestSubject(ModelRestView, extjs.ExtJsMixin):
    class Meta:
        simplified = Subject


@extjs.extjs_modelapi
@restful_api
class RestPeriod(ModelRestView, extjs.ExtJsMixin):
    class Meta:
        simplified = Period
