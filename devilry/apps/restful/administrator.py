from ..simplified.administrator import Node, Subject, Period
from restview import ModelRestView
from restful_api import restful_api


@restful_api
class RestNode(ModelRestView):
    class Meta:
        simplified = Node


@restful_api
class RestSubject(ModelRestView):
    class Meta:
        simplified = Subject


@restful_api
class RestPeriod(ModelRestView):
    class Meta:
        simplified = Period
