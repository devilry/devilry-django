from ...restful import restful_modelapi, ModelRestView
from simplified import Node, Subject, Period


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
