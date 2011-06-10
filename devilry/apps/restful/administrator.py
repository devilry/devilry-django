from ..simplified.administrator import Node
from restview import ModelRestView
from restful_api import restful_api
import extjs


@extjs.extjs_modelapi
@restful_api
class RestNode(ModelRestView, extjs.ExtJsMixin):
    class Meta:
        simplified = Node
