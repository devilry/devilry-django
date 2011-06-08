from ..simplified.administrator import Node
from restview import ModelRestView
from restful_api import restful_api


@restful_api
class RestNode(ModelRestView):
    class Meta:
        simplified = Node
