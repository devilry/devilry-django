from ..simplified.administrator import Node
from restview import RestView
from restful_api import restful_api


@restful_api
class RestNode(RestView):
    class Meta:
        simplified = Node
