
from ..simplified.administrator import Node
import fields
from restview import RestView
from base import GetFormBase


class RestNode(Node, RestView):
    class GetForm(GetFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Node.get_default_ordering())
        deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)

    
