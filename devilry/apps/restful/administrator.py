from ..simplified.administrator import Node, Subject, Period
from restview import ModelRestView
from restful_api import restful_modelapi


@restful_modelapi
class RestNode(ModelRestView):
    class Meta:
        simplified = Node


@restful_modelapi
class RestSubject(ModelRestView):
    class Meta:
        simplified = Subject


@restful_modelapi
class RestPeriod(ModelRestView):
    class Meta:
        simplified = Period
